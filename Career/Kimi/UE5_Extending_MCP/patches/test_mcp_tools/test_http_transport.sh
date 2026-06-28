#!/bin/bash
# MCP HTTP Transport Test Suite (curl-based)
# Usage: ./test_http_transport.sh [PORT] [SESSION_ID]
# If SESSION_ID is not provided, initialize is called first

set -e

PORT=${1:-9877}
URL="http://localhost:${PORT}/jsonrpc"
SESSION_ID=${2:-}

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PASS_COUNT=0
FAIL_COUNT=0

# Helper functions
make_request() {
    local id=$1
    local method=$2
    local params=$3
    
    local headers=(-H "Content-Type: application/json" -H "Accept: text/event-stream")
    if [ -n "$SESSION_ID" ]; then
        headers+=("-H" "Mcp-Session-Id: ${SESSION_ID}")
    fi
    
    curl -s -N "${URL}" \
        "${headers[@]}" \
        -d "{\"jsonrpc\":\"2.0\",\"id\":${id},\"method\":\"${method}\",\"params\":${params}}"
}

test_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASS_COUNT++))
}

test_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAIL_COUNT++))
}

# If no session ID, initialize first
if [ -z "$SESSION_ID" ]; then
    echo "=== Initialize ==="
    INIT_RESP=$(make_request 1 "initialize" '{"protocolVersion":"2025-11-25","capabilities":{}}')
    SESSION_ID=$(echo "$INIT_RESP" | grep -o '"sessionId":"[^"]*"' | cut -d'"' -f4)
    if [ -n "$SESSION_ID" ]; then
        test_pass "initialize (session: $SESSION_ID)"
    else
        test_fail "initialize (no session ID)"
        echo "Response: $INIT_RESP"
        exit 1
    fi
fi

echo ""
echo "=== Test: tools/list ==="
RESPONSE=$(make_request 2 "tools/list" '{}')
if echo "$RESPONSE" | grep -q '"tools"'; then
    TOOL_COUNT=$(echo "$RESPONSE" | grep -o '"name"' | wc -l)
    test_pass "tools/list ($TOOL_COUNT tools found)"
else
    test_fail "tools/list"
    echo "Response: $RESPONSE"
fi

echo ""
echo "=== Test: execute_console_command ==="
RESPONSE=$(make_request 3 "tools/call" '{"name":"execute_console_command","arguments":{"command":"stat fps"}}')
if echo "$RESPONSE" | grep -q '"content"'; then
    test_pass "execute_console_command"
else
    test_fail "execute_console_command"
    echo "Response: $RESPONSE"
fi

echo ""
echo "=== Test: get_editor_context ==="
RESPONSE=$(make_request 4 "tools/call" '{"name":"get_editor_context","arguments":{}}')
if echo "$RESPONSE" | grep -q '"World"'; then
    test_pass "get_editor_context"
else
    test_fail "get_editor_context"
    echo "Response: $RESPONSE"
fi

echo ""
echo "=== Test: capture_viewport ==="
RESPONSE=$(make_request 5 "tools/call" '{"name":"capture_viewport","arguments":{}}')
if echo "$RESPONSE" | grep -q '"image"'; then
    test_pass "capture_viewport"
else
    test_fail "capture_viewport"
    echo "Response: $RESPONSE"
fi

echo ""
echo "=== Test: save_current_level ==="
RESPONSE=$(make_request 6 "tools/call" '{"name":"save_current_level","arguments":{}}')
if echo "$RESPONSE" | grep -q '"content"'; then
    test_pass "save_current_level"
else
    test_fail "save_current_level"
    echo "Response: $RESPONSE"
fi

echo ""
echo "=== Test: ListActors ==="
RESPONSE=$(make_request 7 "tools/call" '{"name":"ListActors","arguments":{}}')
if echo "$RESPONSE" | grep -q '"Actors"'; then
    ACTOR_COUNT=$(echo "$RESPONSE" | grep -o '"Actors"' | wc -l)
    test_pass "ListActors"
else
    test_fail "ListActors"
    echo "Response: $RESPONSE"
fi

echo ""
echo "=== Test: GetActorDetails ==="
# Get first actor name from ListActors
FIRST_ACTOR=$(echo "$RESPONSE" | grep -o '"Name":"[^"]*"' | head -1 | cut -d'"' -f4)
if [ -n "$FIRST_ACTOR" ]; then
    RESPONSE=$(make_request 8 "tools/call" "{\"name\":\"GetActorDetails\",\"arguments\":{\"ActorName\":\"${FIRST_ACTOR}\"}}")
    if echo "$RESPONSE" | grep -q "\"Name\":\"${FIRST_ACTOR}\""; then
        test_pass "GetActorDetails (${FIRST_ACTOR})"
    else
        test_fail "GetActorDetails"
        echo "Response: $RESPONSE"
    fi
else
    test_fail "GetActorDetails (no actor from ListActors)"
fi

echo ""
echo "=== Test: SpawnActor ==="
RESPONSE=$(make_request 9 "tools/call" '{"name":"SpawnActor","arguments":{"ClassName":"PointLight","Location":{"X":0,"Y":0,"Z":500},"Rotation":{"Pitch":0,"Yaw":0,"Roll":0},"Scale":{"X":1,"Y":1,"Z":1}}}')
if echo "$RESPONSE" | grep -q '"bSuccess":true'; then
    SPAWNED_NAME=$(echo "$RESPONSE" | grep -o '"ActorName":"[^"]*"' | cut -d'"' -f4)
    test_pass "SpawnActor (${SPAWNED_NAME})"
else
    test_fail "SpawnActor"
    echo "Response: $RESPONSE"
fi

echo ""
echo "=== Test: DeleteActor ==="
if [ -n "$SPAWNED_NAME" ]; then
    RESPONSE=$(make_request 10 "tools/call" "{\"name\":\"DeleteActor\",\"arguments\":{\"ActorName\":\"${SPAWNED_NAME}\"}}")
    if echo "$RESPONSE" | grep -q '"bSuccess":true'; then
        test_pass "DeleteActor (${SPAWNED_NAME})"
    else
        test_fail "DeleteActor"
        echo "Response: $RESPONSE"
    fi
else
    test_fail "DeleteActor (no spawned actor)"
fi

echo ""
echo "=== Test: SetActorTransform ==="
if [ -n "$FIRST_ACTOR" ]; then
    RESPONSE=$(make_request 11 "tools/call" "{\"name\":\"SetActorTransform\",\"arguments\":{\"ActorName\":\"${FIRST_ACTOR}\",\"Location\":{\"X\":100,\"Y\":200,\"Z\":300},\"Rotation\":{\"Pitch\":0,\"Yaw\":45,\"Roll\":0},\"Scale\":{\"X\":2,\"Y\":2,\"Z\":2}}}")
    if echo "$RESPONSE" | grep -q '"bSuccess":true'; then
        test_pass "SetActorTransform (${FIRST_ACTOR})"
    else
        test_fail "SetActorTransform"
        echo "Response: $RESPONSE"
    fi
else
    test_fail "SetActorTransform (no actor from ListActors)"
fi

echo ""
echo "=== Test: Error Handling ==="
RESPONSE=$(make_request 12 "tools/call" '{"name":"DeleteActor","arguments":{"ActorName":"NonExistentActor_12345"}}')
if echo "$RESPONSE" | grep -q '"bSuccess":false'; then
    test_pass "error_handling (DeleteActor non-existent)"
else
    test_fail "error_handling"
    echo "Response: $RESPONSE"
fi

echo ""
echo "=============================="
echo "  Results: $PASS_COUNT passed, $FAIL_COUNT failed"
echo "=============================="

if [ $FAIL_COUNT -eq 0 ]; then
    exit 0
else
    exit 1
fi
