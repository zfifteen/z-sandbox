#import <Metal/Metal.h>
#import <Foundation/Foundation.h>
#include <sys/utsname.h>
#include <stdint.h>
#ifdef __APPLE__
#include <sys/sysctl.h>
#endif

void z5d_gpu_print_info(void) {
    // Hardware Configuration block
    printf("Hardware Configuration:\n");
    printf("======================\n");

#ifdef __APPLE__
    char cpu_brand[256] = {0};
    size_t cpu_size = sizeof(cpu_brand);
    if (sysctlbyname("machdep.cpu.brand_string", cpu_brand, &cpu_size, NULL, 0) == 0 && cpu_brand[0]) {
        printf("CPU: %s\n", cpu_brand);
    } else {
        printf("CPU: unknown\n");
    }

    uint32_t cores = 0;
    size_t cores_sz = sizeof(cores);
    if (sysctlbyname("hw.ncpu", &cores, &cores_sz, NULL, 0) == 0 && cores > 0) {
        printf("Cores: %u\n", cores);
    } else {
        printf("Cores: unknown\n");
    }

    uint64_t mem_bytes = 0;
    size_t mem_sz = sizeof(mem_bytes);
    if (sysctlbyname("hw.memsize", &mem_bytes, &mem_sz, NULL, 0) == 0 && mem_bytes > 0) {
        unsigned long long gb = (unsigned long long)(mem_bytes / (1024ULL * 1024ULL * 1024ULL));
        printf("Memory: %lluGB\n", gb);
    } else {
        printf("Memory: unknown\n");
    }
#else
    printf("CPU: unknown\n");
    printf("Cores: unknown\n");
    printf("Memory: unknown\n");
#endif

    struct utsname uname_info;
    if (uname(&uname_info) == 0) {
        printf("Architecture: %s\n", uname_info.machine);
        printf("OS: %s %s\n", uname_info.sysname, uname_info.release);
    } else {
        printf("Architecture: unknown\n");
        printf("OS: unknown\n");
    }

    printf("\n=== Metal GPU Info ===\n");

    @autoreleasepool {
        id<MTLDevice> device = MTLCreateSystemDefaultDevice();
        if (!device) {
            printf("Metal GPU not available.\n");
            printf("======================\n");
            return;
        }

        MTLSize tg = device.maxThreadsPerThreadgroup;

        printf("Name: %s\n", device.name.UTF8String);
        printf("RegistryID: 0x%llx\n", (unsigned long long)device.registryID);
        printf("Unified Memory: %s\n", device.hasUnifiedMemory ? "yes" : "no");
        printf("Low Power: %s\n", device.isLowPower ? "yes" : "no");
        printf("Headless: %s\n", device.isHeadless ? "yes" : "no");
        printf("Removable: %s\n", device.isRemovable ? "yes" : "no");
        printf("Max threads per threadgroup: %llu x %llu x %llu\n",
               (unsigned long long)tg.width,
               (unsigned long long)tg.height,
               (unsigned long long)tg.depth);
        if ([device respondsToSelector:@selector(recommendedMaxWorkingSetSize)]) {
            printf("Recommended Max Working Set: %llu bytes\n",
                   (unsigned long long)device.recommendedMaxWorkingSetSize);
        }
        printf("======================\n");
    }
}
