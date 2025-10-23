#!/bin/bash
# Demo script for hyper-rotation messenger
# Runs sender and receiver in separate terminal panes
#
# ⚠️ RESEARCH PROOF OF CONCEPT ONLY ⚠️
# This is experimental research code for exploring mathematical concepts.
# NOT for production use or real communications.

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${RED}⚠️  RESEARCH PROOF OF CONCEPT ONLY ⚠️${NC}"
echo -e "${RED}This is experimental research code. NOT for production use.${NC}"
echo ""
echo -e "${YELLOW}=== Hyper-Rotation Messenger Demo ===${NC}"
echo ""
echo "This demo runs a local sender and receiver with 3-second key rotation."
echo ""

# Check if tmux is available
if command -v tmux &> /dev/null; then
    echo -e "${GREEN}Using tmux for split-pane demo${NC}"
    echo ""
    
    # Kill existing session if it exists
    tmux kill-session -t hr_demo 2>/dev/null || true
    
    # Create new session with receiver
    tmux new-session -d -s hr_demo -n "HR Demo"
    
    # Split horizontally
    tmux split-window -h -t hr_demo
    
    # Run receiver in left pane
    tmux send-keys -t hr_demo:0.0 "cd $SCRIPT_DIR/../.. && python3 apps/hr_cli/recv.py --rotation 3" C-m
    
    # Wait for receiver to start
    sleep 1
    
    # Run sender in right pane
    tmux send-keys -t hr_demo:0.1 "cd $SCRIPT_DIR/../.. && python3 apps/hr_cli/send.py --rotation 3" C-m
    
    # Attach to session
    tmux attach-session -t hr_demo
    
elif command -v screen &> /dev/null; then
    echo -e "${GREEN}Using screen for split-pane demo${NC}"
    echo ""
    
    # Kill existing session if it exists
    screen -S hr_demo -X quit 2>/dev/null || true
    
    # Create new screen session
    screen -dmS hr_demo
    
    # Start receiver
    screen -S hr_demo -X screen -t receiver bash -c "cd $SCRIPT_DIR/../.. && python3 apps/hr_cli/recv.py --rotation 3"
    
    # Wait for receiver to start
    sleep 1
    
    # Start sender
    screen -S hr_demo -X screen -t sender bash -c "cd $SCRIPT_DIR/../.. && python3 apps/hr_cli/send.py --rotation 3"
    
    # Attach to session
    screen -r hr_demo
    
else
    echo -e "${YELLOW}Neither tmux nor screen available.${NC}"
    echo "Running simple sequential demo instead..."
    echo ""
    
    # Simple sequential demo
    echo -e "${BLUE}Starting receiver in background...${NC}"
    cd "$SCRIPT_DIR/../.."
    python3 apps/hr_cli/recv.py --rotation 3 &
    RECV_PID=$!
    
    # Wait for receiver to start
    sleep 2
    
    echo -e "${BLUE}Starting sender...${NC}"
    echo "Type messages to send (Ctrl+C to exit)"
    echo ""
    
    # Run sender in foreground
    python3 apps/hr_cli/send.py --rotation 3
    
    # Kill receiver when done
    kill $RECV_PID 2>/dev/null || true
fi
