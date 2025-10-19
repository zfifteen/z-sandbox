#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <errno.h>
#include <getopt.h>
#include <dirent.h>
#include <openssl/rsa.h>
#include <openssl/pem.h>
#include <openssl/bn.h>

#include "z5d_factorization_shortcut.h"

#ifndef MIN
#define MIN(a,b) ((a) < (b) ? (a) : (b))
#endif
#ifndef MAX
#define MAX(a,b) ((a) > (b) ? (a) : (b))
#endif

typedef struct {
    char *key_path;
    char *cert_path;
    char *modulus_dec;
} key_info_t;

typedef struct {
    char **items;
    int count;
} file_list_t;

static double elapsed_seconds(struct timeval start, struct timeval end) {
    return (double)(end.tv_sec - start.tv_sec) + (double)(end.tv_usec - start.tv_usec) / 1e6;
}

static char *trim_line(char *line) {
    size_t len = strlen(line);
    while (len > 0 && (line[len - 1] == '\n' || line[len - 1] == '\r')) {
        line[len - 1] = '\0';
        len--;
    }
    return line;
}

static void ensure_directory(const char *path) {
    struct stat st;
    if (stat(path, &st) == -1) {
        if (mkdir(path, 0700) == -1 && errno != EEXIST) {
            fprintf(stderr, "❌ Failed to create directory %s: %s\n", path, strerror(errno));
            exit(1);
        }
    } else if (!S_ISDIR(st.st_mode)) {
        fprintf(stderr, "❌ %s exists and is not a directory\n", path);
        exit(1);
    }
}

static void init_file_list(file_list_t *list) {
    list->items = NULL;
    list->count = 0;
}

static void free_file_list(file_list_t *list) {
    if (!list) return;
    if (list->items) {
        for (int i = 0; i < list->count; ++i) {
            free(list->items[i]);
        }
        free(list->items);
    }
    list->items = NULL;
    list->count = 0;
}

static int collect_files_with_suffix(const char *dir_path, const char *suffix, file_list_t *list) {
    DIR *dir = opendir(dir_path);
    if (!dir) {
        return -1;
    }

    struct dirent *ent;
    size_t suffix_len = strlen(suffix);
    int capacity = 0;

    while ((ent = readdir(dir)) != NULL) {
        const char *name = ent->d_name;
        size_t len = strlen(name);
        if (len > suffix_len && strcmp(name + len - suffix_len, suffix) == 0) {
            if (list->count == capacity) {
                capacity = capacity ? capacity * 2 : 8;
                char **new_items = realloc(list->items, sizeof(char *) * capacity);
                if (!new_items) {
                    closedir(dir);
                    return -1;
                }
                list->items = new_items;
            }
            list->items[list->count++] = strdup(name);
        }
    }

    closedir(dir);
    return 0;
}

static char *find_new_file(const file_list_t *before, const file_list_t *after) {
    for (int i = 0; i < after->count; ++i) {
        int found = 0;
        for (int j = 0; j < before->count; ++j) {
            if (strcmp(after->items[i], before->items[j]) == 0) {
                found = 1;
                break;
            }
        }
        if (!found) {
            return strdup(after->items[i]);
        }
    }
    return NULL;
}

static int run_z5d_generator(char **key_path_out, char **cert_path_out) {
    file_list_t before_keys;
    file_list_t before_certs;
    init_file_list(&before_keys);
    init_file_list(&before_certs);

    if (collect_files_with_suffix("generated", ".key", &before_keys) != 0 ||
        collect_files_with_suffix("generated", ".crt", &before_certs) != 0) {
        fprintf(stderr, "❌ Unable to scan generated directory before run\n");
        free_file_list(&before_keys);
        free_file_list(&before_certs);
        return -1;
    }

    FILE *pipe = popen("./z5d_secure_key_gen --quiet", "r");
    if (!pipe) {
        perror("popen z5d_secure_key_gen");
        free_file_list(&before_keys);
        free_file_list(&before_certs);
        return -1;
    }

    char buffer[1024];
    while (fgets(buffer, sizeof(buffer), pipe) != NULL) {
        char *line = trim_line(buffer);
        if (*line) {
            printf("%s\n", line);
        }
    }

    int status = pclose(pipe);
    if (status == -1) {
        fprintf(stderr, "❌ Failed to execute z5d_secure_key_gen\n");
        free_file_list(&before_keys);
        free_file_list(&before_certs);
        return -1;
    }

    file_list_t after_keys;
    file_list_t after_certs;
    init_file_list(&after_keys);
    init_file_list(&after_certs);

    if (collect_files_with_suffix("generated", ".key", &after_keys) != 0 ||
        collect_files_with_suffix("generated", ".crt", &after_certs) != 0) {
        fprintf(stderr, "❌ Unable to scan generated directory after run\n");
        free_file_list(&before_keys);
        free_file_list(&before_certs);
        free_file_list(&after_keys);
        free_file_list(&after_certs);
        return -1;
    }

    char *new_key = find_new_file(&before_keys, &after_keys);
    char *new_cert = find_new_file(&before_certs, &after_certs);

    free_file_list(&before_keys);
    free_file_list(&before_certs);
    free_file_list(&after_keys);
    free_file_list(&after_certs);

    if (!new_key) {
        fprintf(stderr, "❌ Could not identify generated key file\n");
        free(new_cert);
        return -1;
    }

    size_t path_len = strlen("generated/") + strlen(new_key) + 1;
    char *key_path = malloc(path_len);
    if (!key_path) {
        free(new_key);
        free(new_cert);
        fprintf(stderr, "❌ Memory allocation failure\n");
        return -1;
    }
    snprintf(key_path, path_len, "generated/%s", new_key);
    free(new_key);

    char *cert_path = NULL;
    if (new_cert) {
        path_len = strlen("generated/") + strlen(new_cert) + 1;
        cert_path = malloc(path_len);
        if (cert_path) {
            snprintf(cert_path, path_len, "generated/%s", new_cert);
        }
        free(new_cert);
    }

    *key_path_out = key_path;
    if (cert_path_out) {
        *cert_path_out = cert_path;
    } else if (cert_path) {
        free(cert_path);
    }

    return 0;
}

static char *extract_modulus_decimal(const char *key_path) {
    FILE *fp = fopen(key_path, "r");
    if (!fp) {
        fprintf(stderr, "❌ Unable to open key file %s: %s\n", key_path, strerror(errno));
        return NULL;
    }

    RSA *rsa = PEM_read_RSAPrivateKey(fp, NULL, NULL, NULL);
    fclose(fp);
    if (!rsa) {
        fprintf(stderr, "❌ Failed to parse RSA private key %s\n", key_path);
        return NULL;
    }

    const BIGNUM *n = NULL;
    RSA_get0_key(rsa, &n, NULL, NULL);
    char *dec = BN_bn2dec(n);
    RSA_free(rsa);
    if (!dec) {
        fprintf(stderr, "❌ Failed to convert modulus to decimal\n");
        return NULL;
    }
    char *dup = strdup(dec);
    OPENSSL_free(dec);
    return dup;
}

static void delete_file_if_exists(const char *path) {
    if (!path) return;
    if (unlink(path) == 0) {
        printf("  Removed: %s\n", path);
    }
}

static int compare_ints(const void *a, const void *b) {
    int lhs = *(const int *)a;
    int rhs = *(const int *)b;
    return (lhs > rhs) - (lhs < rhs);
}

static void analyze_and_report(char **moduli, int count) {
    if (count == 0) {
        printf("❌ No moduli to analyze\n");
        return;
    }

    size_t decimal_places = 0;
    for (int i = 0; i < count; ++i) {
        size_t len = strlen(moduli[i]);
        if (len > decimal_places) {
            decimal_places = len;
        }
    }

    int grid_size = (int)MAX(8, decimal_places / 2);
    size_t sample_len = strlen(moduli[0]);
    printf("\nANALYZING %d RSA MODULI\n", count);
    printf("=============================================\n");
    printf("Sample modulus: %.50s...%.20s\n", moduli[0], moduli[0] + (sample_len > 20 ? sample_len - 20 : 0));
    printf("Decimal places: %zu\n", decimal_places);
    printf("Calculated grid size: %zu\n", decimal_places / 2);
    printf("Actual grid size: %d×%d\n", grid_size, grid_size);
    printf("Total grid cells: %d\n\n", grid_size * grid_size);

    int *counts = calloc(grid_size * grid_size, sizeof(int));
    int *x_coords = malloc(sizeof(int) * count);
    int *y_coords = malloc(sizeof(int) * count);
    if (!counts || !x_coords || !y_coords) {
        fprintf(stderr, "❌ Memory allocation failure during analysis\n");
        free(counts);
        free(x_coords);
        free(y_coords);
        return;
    }

    size_t mid = decimal_places / 2;
    for (int i = 0; i < count; ++i) {
        const char *mod = moduli[i];
        size_t len = strlen(mod);
        size_t pad = decimal_places > len ? decimal_places - len : 0;

        char *buffer = malloc(decimal_places + 1);
        memset(buffer, '0', pad);
        memcpy(buffer + pad, mod, len);
        buffer[decimal_places] = '\0';

        int x = 0;
        int y = 0;
        for (size_t idx = 0; idx < mid; ++idx) {
            x = (x * 10 + (buffer[idx] - '0')) % grid_size;
        }
        for (size_t idx = mid; idx < decimal_places; ++idx) {
            y = (y * 10 + (buffer[idx] - '0')) % grid_size;
        }

        free(buffer);
        x_coords[i] = x;
        y_coords[i] = y;
        counts[y * grid_size + x] += 1;
    }

    int unique_cells = 0;
    int max_density = 0;
    for (int idx = 0; idx < grid_size * grid_size; ++idx) {
        if (counts[idx] > 0) {
            unique_cells++;
            if (counts[idx] > max_density) {
                max_density = counts[idx];
            }
        }
    }

    double avg_density = unique_cells > 0 ? (double)count / unique_cells : 0.0;

    int *densities = NULL;
    if (unique_cells > 0) {
        densities = malloc(sizeof(int) * unique_cells);
        int pos = 0;
        for (int idx = 0; idx < grid_size * grid_size; ++idx) {
            if (counts[idx] > 0) {
                densities[pos++] = counts[idx];
            }
        }
        qsort(densities, unique_cells, sizeof(int), compare_ints);
    }

    double threshold = 0.0;
    if (unique_cells > 0) {
        if (unique_cells % 2 == 1) {
            threshold = densities[unique_cells / 2];
        } else {
            threshold = (densities[unique_cells / 2 - 1] + densities[unique_cells / 2]) / 2.0;
        }
    }

    int high_density_cells = 0;
    int captured_moduli = 0;
    for (int idx = 0; idx < grid_size * grid_size; ++idx) {
        int count_here = counts[idx];
        if (count_here > 0) {
            if ((double)count_here >= threshold) {
                high_density_cells++;
                captured_moduli += count_here;
            }
        }
    }

    double total_cells = (double)grid_size * grid_size;
    double reduction_percent = total_cells > 0.0 ? (1.0 - (double)high_density_cells / total_cells) * 100.0 : 0.0;
    double grid_utilization = total_cells > 0.0 ? (double)unique_cells / total_cells * 100.0 : 0.0;
    double search_multiplier = total_cells > 0.0 ? (double)high_density_cells / total_cells : 0.0;
    double capture_rate = count > 0 ? (double)captured_moduli / count * 100.0 : 0.0;
    int compression_ratio = search_multiplier > 0.0 ? (int)(1.0 / search_multiplier) : 0;

    printf("GRID ANALYSIS RESULTS:\n");
    printf("  Grid utilization: %.1f%% (%d/%d cells)\n", grid_utilization, unique_cells, grid_size * grid_size);
    printf("  Density stats: avg=%.1f, max=%d\n", avg_density, max_density);
    printf("  50%%ile threshold: %.1f\n", threshold);
    printf("  High-density cells: %d\n", high_density_cells);
    printf("  Reduction: %.2f%%\n", reduction_percent);
    printf("  Capture rate: %.1f%%\n", capture_rate);
    printf("  Search multiplier: %.6fx\n", search_multiplier);
    printf("  Compression ratio: %d:1\n", compression_ratio);

    if (capture_rate >= 99.9) {
        printf("  Status: ✓ Perfect\n");
    } else {
        printf("  Status: ~ %.0f%%\n", capture_rate);
    }

    free(counts);
    free(x_coords);
    free(y_coords);
    free(densities);
}

int main(int argc, char **argv) {
    int key_count = 1;
    int keep_files = 0;
    int factor_shortcut = 0;
    int shortcut_iterations = 200;
    double shortcut_epsilon = 0.02;

    static struct option long_options[] = {
        {"keys", required_argument, 0, 'k'},
        {"keep-files", no_argument, 0, 'f'},
        {"factor-shortcut", no_argument, 0, 's'},
        {"shortcut-iters", required_argument, 0, 'i'},
        {"shortcut-eps", required_argument, 0, 'e'},
        {0, 0, 0, 0}
    };

    int opt;
    int option_index = 0;
    while ((opt = getopt_long(argc, argv, "", long_options, &option_index)) != -1) {
        switch (opt) {
            case 'k':
                key_count = atoi(optarg);
                if (key_count <= 0) key_count = 1;
                break;
            case 'f':
                keep_files = 1;
                break;
            case 's':
                factor_shortcut = 1;
                break;
            case 'i':
                shortcut_iterations = atoi(optarg);
                if (shortcut_iterations < 1) shortcut_iterations = 1;
                break;
            case 'e':
                shortcut_epsilon = atof(optarg);
                if (shortcut_epsilon <= 0.0) shortcut_epsilon = 0.02;
                break;
            default:
                fprintf(stderr, "Usage: %s [--keys N] [--keep-files]\n", argv[0]);
                return 1;
        }
    }

    printf("Z5D RSA PRIME GRID ANALYSIS (C Edition)\n");
    printf("===================================\n");
    printf("WARNING: FOR EDUCATIONAL USE ONLY\n");
    printf("Target: Generate %d RSA-4096 key(s)\n\n", key_count);

    ensure_directory("generated");

    key_info_t *infos = calloc(key_count, sizeof(key_info_t));
    if (!infos) {
        fprintf(stderr, "❌ Memory allocation failure\n");
        return 1;
    }

    struct timeval total_start, total_end;
    gettimeofday(&total_start, NULL);

    int shortcut_successes = 0;

    for (int i = 0; i < key_count; ++i) {
        struct timeval start, end;
        printf("  Generating key %d/%d... ", i + 1, key_count);
        fflush(stdout);
        gettimeofday(&start, NULL);
        if (run_z5d_generator(&infos[i].key_path, &infos[i].cert_path) != 0) {
            free(infos);
            return 1;
        }
        gettimeofday(&end, NULL);
        printf("✓ (%.1fs)\n", elapsed_seconds(start, end));

        printf("Extracting modulus from key %d... ", i + 1);
        fflush(stdout);
        gettimeofday(&start, NULL);
        infos[i].modulus_dec = extract_modulus_decimal(infos[i].key_path);
        gettimeofday(&end, NULL);
        if (!infos[i].modulus_dec) {
            free(infos);
            return 1;
        }
        size_t digits = strlen(infos[i].modulus_dec);
        printf("✓ (%zu digits, %.3fs)\n", digits, elapsed_seconds(start, end));

        if (factor_shortcut) {
            z5d_factor_stat_t stat;
            int rc = z5d_factorization_shortcut(infos[i].modulus_dec,
                                                shortcut_iterations,
                                                shortcut_epsilon,
                                                &stat);
            if (rc == 1 && stat.success) {
                shortcut_successes++;
                printf("    ↳ Shortcut success after %d divisions (%.2fs)\n",
                       stat.divisions_tried, stat.elapsed_seconds);
                if (stat.factor_p && stat.factor_q) {
                    size_t p_len = strlen(stat.factor_p);
                    size_t q_len = strlen(stat.factor_q);
                    printf("       p ≈ %.*s... (len=%zu)\n",
                           20, stat.factor_p, p_len);
                    printf("       q ≈ %.*s... (len=%zu)\n",
                           20, stat.factor_q, q_len);
                }
            } else {
                printf("    ↳ Shortcut attempt failed after %d divisions (%.2fs)\n",
                       stat.divisions_tried, stat.elapsed_seconds);
            }
            z5d_factorization_free(&stat);
        }
    }

    gettimeofday(&total_end, NULL);

    char **moduli = malloc(sizeof(char *) * key_count);
    if (!moduli) {
        fprintf(stderr, "❌ Memory allocation failure\n");
        free(infos);
        return 1;
    }
    for (int i = 0; i < key_count; ++i) {
        moduli[i] = infos[i].modulus_dec;
    }

    analyze_and_report(moduli, key_count);

    double total_time = elapsed_seconds(total_start, total_end);
    printf("\n============================================================\n");
    printf("Z5D RSA MODULI GRID ANALYSIS SUMMARY (C)\n");
    printf("============================================================\n");
    printf("Keys generated: %d\n", key_count);
    printf("Moduli analyzed: %d\n", key_count);
    printf("Total pipeline time: %.1fs\n", total_time);
    printf("\nEducational demonstration: Adaptive grid filtering on authentic RSA moduli\n");

    if (factor_shortcut) {
        printf("Shortcut successes: %d/%d (ε=%.3f, max_iters=%d)\n",
               shortcut_successes, key_count, shortcut_epsilon, shortcut_iterations);
    }

    if (!keep_files) {
        printf("\nCleaning up %d generated files...\n", key_count);
        for (int i = 0; i < key_count; ++i) {
            delete_file_if_exists(infos[i].key_path);
            delete_file_if_exists(infos[i].cert_path);
        }
    }

    for (int i = 0; i < key_count; ++i) {
        free(infos[i].key_path);
        free(infos[i].cert_path);
        free(infos[i].modulus_dec);
    }
    free(moduli);
    free(infos);

    return 0;
}
