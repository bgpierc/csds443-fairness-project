#!/bin/bash
# compare different carbon prices

echo "=========================================="
echo "Carbon Price Impact Analysis"
echo "=========================================="
echo ""

for price in 0 25 50 100 200; do
    echo "---------- Carbon Price: \$$price/ton ----------"
    python simple_brownfield_model.py ./ercot_brownfield_expansion/10_days 2 glpk $price 2>&1 | \
        grep -E "(Total System Cost|Total CO2|naturalgas|conventional_steam_coal|onshore_wind|utilitypv)" | \
        head -8
    echo ""
done
