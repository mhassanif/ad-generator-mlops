
echo "========================================="
echo "Step 3: Generating Traffic (20 requests)"
echo "========================================="
for i in {1..20}; do
  curl -s -X POST "http://localhost:8000/predict" \
    -H "Content-Type: application/json" \
    -d "{\"brand\": \"Brand$i\", \"product_name\": \"Product$i\"}" > /dev/null
  echo "✓ Request $i sent"
  sleep 0.5
done
