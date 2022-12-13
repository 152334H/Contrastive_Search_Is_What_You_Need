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
  if not data['use_8bit']: continue
  name = data['model_name'].split('/')[-1]
  if 'pythia' not in name: continue
  _, sz, *dedupe = name.split('-')
  results[sz][len(dedupe) == 0] = data["isotropy"]
SIZES = ['19m', '125m', '350m', '800m', '1.3b', '2.7b', '6.7b', '13b']

import matplotlib.pyplot as plt
import numpy as np
plt.style.use('ggplot')


x = np.arange(len(SIZES))  # the label locations
width = 0.35  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - width/2, [results[sz][0] for sz in SIZES], width, label='dedupe')
rects2 = ax.bar(x + width/2, [results[sz][1] for sz in SIZES], width, label='normal')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Isotropy')
ax.set_title('Isotropy by model & dtype')
ax.set_xticks(x, SIZES)
ax.legend()

ax.bar_label(rects1, padding=3)
ax.bar_label(rects2, padding=3)

fig.tight_layout()

plt.savefig("graph2.png")

