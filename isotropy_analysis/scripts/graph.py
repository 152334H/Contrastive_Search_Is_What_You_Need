from pathlib import Path
from json import loads
from collections import defaultdict
json_folder = Path('../inference_results/en/')
TRUNC = '_isotropy_result'
data_dict = {
  "models": [],
  "int8": [],
  "fp16/32": [],
}

results = defaultdict(lambda: [0,0])
for f in json_folder.iterdir():
  data = loads(f.read_bytes())[0]
  results[data["model_name"].split('/')[-1]][data["use_8bit"]] = data["isotropy"]
del results['GPT-J-6B-PNY']

import matplotlib.pyplot as plt
import numpy as np


x = np.arange(len(results))  # the label locations
width = 0.35  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - width/2, [ls[0] for ls in results.values()], width, label='fp16/32')
rects2 = ax.bar(x + width/2, [ls[1] for ls in results.values()], width, label='int8')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Isotropy')
ax.set_title('Isotropy by model & dtype')
ax.set_xticks(x, results.keys())
ax.legend()

ax.bar_label(rects1, padding=3)
ax.bar_label(rects2, padding=3)

fig.tight_layout()

plt.savefig("graph.png")

