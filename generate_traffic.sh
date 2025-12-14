#!/bin/bash
#
# Generate API traffic for testing Grafana metrics
#

echo "🚀 Generating API traffic for Grafana metrics..."
echo "Watch your Grafana dashboard at: http://localhost:3000"
echo ""

# Array of sample products
brands=("Nike" "Adidas" "Apple" "Samsung" "Sony" "Dell" "HP" "Microsoft" "Google" "Amazon")
products=("Running Shoes" "Smart Watch" "Laptop" "Headphones" "Phone" "Tablet" "Monitor" "Keyboard" "Mouse" "Speaker")

for i in {1..20}; do
  # Pick random brand and product
  brand="${brands[$RANDOM % ${#brands[@]}]}"
  product="${products[$RANDOM % ${#products[@]}]}"
  
  echo "[$i/20] Requesting: $brand - $product"
  
  curl -s -X POST "http://localhost:8000/predict" \
    -H "Content-Type: application/json" \
    -d "{\"brand\": \"$brand\", \"product_name\": \"$product\"}" | jq -r '.creative'
  
  echo ""
  sleep 2
done

echo "✅ Done! Generated 20 requests"
echo "📊 Check Grafana dashboard: http://localhost:3000/d/ad-creative-api"
echo "📈 Check Prometheus: http://localhost:9090"
