#!/usr/bin/env sh
set -eu

BACKEND_URL="${BACKEND_URL:-https://backend-production-4652.up.railway.app}"
FRONTEND_URL="${FRONTEND_URL:-https://frontend-production-834c.up.railway.app}"
EXPECTED_VERSION="${EXPECTED_VERSION:-knowledge-v11}"
QUERY="${QUERY:-coherencia textual progresion conectores lector borrador}"
TMP_DIR="$(mktemp -d)"

echo "backend: $BACKEND_URL"
echo "frontend: $FRONTEND_URL"

curl -fsS "$BACKEND_URL/health" -o "$TMP_DIR/health.json"
python3 -c 'import json, sys; payload=json.load(open(sys.argv[1])); assert payload == {"status": "ok"}; print("health ok")' "$TMP_DIR/health.json"

curl -fsS "$BACKEND_URL/security/status" -o "$TMP_DIR/security.json"
python3 -c 'import json, sys; payload=json.load(open(sys.argv[1])); assert payload["security_model"] == "local-first"; assert "authentication" in payload["missing_production_controls"]; assert "rate_limiting" in payload["missing_production_controls"]; assert "DATABASE_URL" not in str(payload); print("security status ok")' "$TMP_DIR/security.json"

curl -fsS "$BACKEND_URL/knowledge/status" -o "$TMP_DIR/knowledge-status.json"
python3 -c 'import json, sys; payload=json.load(open(sys.argv[1])); expected=sys.argv[2]; assert payload["state"] == "published"; assert payload["version"] == expected, payload; print("knowledge status ok", payload["version"])' "$TMP_DIR/knowledge-status.json" "$EXPECTED_VERSION"

curl -fsS -X OPTIONS "$BACKEND_URL/knowledge/query" \
  -H "Origin: $FRONTEND_URL" \
  -H "Access-Control-Request-Method: POST" \
  -D "$TMP_DIR/cors.headers" \
  -o /dev/null
python3 -c 'import sys; headers=open(sys.argv[1]).read().lower(); origin=sys.argv[2].lower(); assert "access-control-allow-origin: " + origin in headers; print("cors ok")' "$TMP_DIR/cors.headers" "$FRONTEND_URL"

curl -fsS -X POST "$BACKEND_URL/knowledge/query" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"$QUERY\",\"version\":\"latest\",\"limit\":3}" \
  -o "$TMP_DIR/query.json"
python3 -c 'import json, sys; payload=json.load(open(sys.argv[1])); expected=sys.argv[2]; assert payload["status"] == "ok"; assert payload["resolved_version"] == payload["version"] == expected, payload; assert payload["cards"]; print("query ok", payload["resolved_version"], payload["cards"][0]["id"])' "$TMP_DIR/query.json" "$EXPECTED_VERSION"

curl -fsSI "$FRONTEND_URL/" -o "$TMP_DIR/frontend.headers"
python3 -c 'import sys; headers=open(sys.argv[1]).read().lower(); assert "200" in headers.splitlines()[0]; assert "content-type: text/html" in headers; print("frontend ok")' "$TMP_DIR/frontend.headers"

echo "production smoke ok"
