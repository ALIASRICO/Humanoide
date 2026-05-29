#!/bin/bash
# Test all Isaac Sim scenes headlessly.
# Runs each scene, waits for "create dds success" (pass) or TIMEOUT (fail).
# Usage: bash simulacion/isaac_sim/test_all_scenes.sh
# Run from repo root: /home/udc/Unitree_G1

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ISAAC_SIM_DIR="$REPO_ROOT/simulacion/isaac_sim"
LOG_DIR="/tmp/isaac_sim_tests"
TIMEOUT=120

mkdir -p "$LOG_DIR"

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate isaaclab

export PYTHONPATH="$ISAAC_SIM_DIR${PYTHONPATH:+:$PYTHONPATH}"

# Force the cyclonedds Python _clayer.so to load the local CycloneDDS build
# (compiled with ENABLE_SHM=0 — no iceoryx) instead of ROS2-Jazzy's
# libddsc.so.0 (which has iceoryx enabled and crashes with stale /dev/shm/ad_*
# segments left by previous SIGKILL'd processes).
# This also prevents the ~420-second silent hang inside app.update() caused by
# CycloneDDS blocking on RouDi registration with stale gsystem_shm.
CYCLONEDDS_NO_IOX_LIB="/home/udc/Humanoide/G1/humanoide/cyclonedds/install/lib"
export LD_LIBRARY_PATH="${CYCLONEDDS_NO_IOX_LIB}${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

# Belt-and-suspenders: also tell CycloneDDS (whichever copy loads) to disable
# iceoryx via config. Use inline XML so no file I/O race on test startup.
export CYCLONEDDS_URI='<CycloneDDS><Domain id="any"><SharedMemory><Enable>false</Enable></SharedMemory></Domain></CycloneDDS>'

declare -A TASKS
TASKS=(
    ["cylinder_dex1"]="Isaac-PickPlace-Cylinder-G129-Dex1-Joint --enable_dex1_dds"
    ["cylinder_dex3"]="Isaac-PickPlace-Cylinder-G129-Dex3-Joint --enable_dex3_dds"
    ["cylinder_inspire"]="Isaac-PickPlace-Cylinder-G129-Inspire-Joint --enable_inspire_dds"
    ["redblock_dex1"]="Isaac-PickPlace-RedBlock-G129-Dex1-Joint --enable_dex1_dds"
    ["redblock_dex3"]="Isaac-PickPlace-RedBlock-G129-Dex3-Joint --enable_dex3_dds"
    ["redblock_inspire"]="Isaac-PickPlace-RedBlock-G129-Inspire-Joint --enable_inspire_dds"
    ["stack_dex1"]="Isaac-Stack-RgyBlock-G129-Dex1-Joint --enable_dex1_dds"
    ["stack_dex3"]="Isaac-Stack-RgyBlock-G129-Dex3-Joint --enable_dex3_dds"
    ["stack_inspire"]="Isaac-Stack-RgyBlock-G129-Inspire-Joint --enable_inspire_dds"
    ["drawer_dex1"]="Isaac-Pick-Redblock-Into-Drawer-G129-Dex1-Joint --enable_dex1_dds"
    ["drawer_dex3"]="Isaac-Pick-Redblock-Into-Drawer-G129-Dex3-Joint --enable_dex3_dds"
    ["move_dex1"]="Isaac-Move-Cylinder-G129-Dex1-Wholebody --enable_dex1_dds"
    ["move_dex3"]="Isaac-Move-Cylinder-G129-Dex3-Wholebody --enable_dex3_dds"
    ["move_inspire"]="Isaac-Move-Cylinder-G129-Inspire-Wholebody --enable_inspire_dds"
)

ORDER=(
    cylinder_dex1 cylinder_dex3 cylinder_inspire
    redblock_dex1 redblock_dex3 redblock_inspire
    stack_dex1 stack_dex3 stack_inspire
    drawer_dex1 drawer_dex3
    move_dex1 move_dex3 move_inspire
)

PASS=()
FAIL=()

for alias in "${ORDER[@]}"; do
    val="${TASKS[$alias]}"
    task="${val%% *}"
    hand="${val#* }"

    log="$LOG_DIR/${alias}.log"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Testing: $alias"
    echo "  Task:    $task"
    echo "  Log:     $log"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Clean stale Carbonite/Isaac shared-memory from previous killed processes
    rm -f /dev/shm/carb-* /dev/shm/sem.carb-* /dev/shm/sem.carbonite-* /dev/shm/isaac_* 2>/dev/null
    # Zero small iceoryx metadata segments (gsystem_shm, lsystem_shm, mutex, connect_queue).
    # Zeroing gsystem_shm clears the RouDi magic-number so new iceoryx clients see
    # "no RouDi" and fall back gracefully.  SAFETY: skip any file > 2 MB to avoid
    # accidentally zeroing a large data segment (which could take minutes at ~200 MB/s).
    for _f in /dev/shm/ad_*; do
        [ -f "$_f" ] || continue
        _sz=$(stat -c%s "$_f" 2>/dev/null || echo 999999999)
        [ "$_sz" -le 2097152 ] && dd if=/dev/zero of="$_f" bs="$_sz" count=1 2>/dev/null || true
    done

    python "$ISAAC_SIM_DIR/sim_main.py" \
        --task "$task" \
        --action_source dds \
        --enable_cameras \
        $hand \
        --robot_type g129 \
        --headless \
        --no_image_server \
        --skip_stiffness_check \
        > "$log" 2>&1 &
    PID=$!

    elapsed=0
    result="TIMEOUT"
    while [ $elapsed -lt $TIMEOUT ]; do
        # Success
        if grep -q "create dds success" "$log" 2>/dev/null; then
            result="PASS"
            break
        fi
        # Hard Python failure (not benign MDL/material warnings)
        if grep -qE "^Traceback|ModuleNotFoundError|ImportError|AssertionError: " "$log" 2>/dev/null; then
            result="FAIL"
            break
        fi
        # Process exited on its own (crash, e.g. C assertion) before reaching success
        if ! kill -0 "$PID" 2>/dev/null; then
            result="CRASH"
            grep -q "create dds success" "$log" 2>/dev/null && result="PASS"
            break
        fi
        sleep 5
        elapsed=$((elapsed + 5))
        _cur_lines=$(wc -l < "$log" 2>/dev/null || echo 0)
        printf "  ... %ds/%ds  [%d lines]\r" "$elapsed" "$TIMEOUT" "$_cur_lines"
    done
    echo ""  # newline after progress

    kill -9 $PID 2>/dev/null
    pkill -9 -f "sim_main.py" 2>/dev/null
    sleep 3
    # Clean stale shared-memory left by killed process
    rm -f /dev/shm/carb-* /dev/shm/sem.carb-* /dev/shm/sem.carbonite-* /dev/shm/isaac_* 2>/dev/null
    # Zero small iceoryx segments (same 2 MB safety cap as above)
    for _f in /dev/shm/ad_*; do
        [ -f "$_f" ] || continue
        _sz=$(stat -c%s "$_f" 2>/dev/null || echo 999999999)
        [ "$_sz" -le 2097152 ] && dd if=/dev/zero of="$_f" bs="$_sz" count=1 2>/dev/null || true
    done

    if [ "$result" = "PASS" ]; then
        PASS+=("$alias")
        echo "  → PASS"
    else
        FAIL+=("$alias")
        echo "  → $result  (see $log)"
        echo "  Last 8 lines:"
        tail -8 "$log" | sed 's/^/    /'
    fi
done

echo ""
echo "════════════════════════════════════════"
echo "  RESULTADOS FINALES"
echo "════════════════════════════════════════"
echo ""
echo "  PASS (${#PASS[@]}):"
for t in "${PASS[@]}"; do echo "    ✓ $t"; done
echo ""
echo "  FAIL/TIMEOUT (${#FAIL[@]}):"
for t in "${FAIL[@]}"; do echo "    ✗ $t  →  $LOG_DIR/${t}.log"; done
echo ""
