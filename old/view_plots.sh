#!/bin/bash
# open all generated plots

echo "Opening plots..."
for plot in plots/*.png; do
    open "$plot" 2>/dev/null || xdg-open "$plot" 2>/dev/null || echo "Cannot open $plot - please view manually"
done

echo ""
echo "Generated plots:"
ls -1 plots/
