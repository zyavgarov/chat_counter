import numpy as np
import pandas as pd

chat = pd.read_json('result.json')
messages = chat["messages"]
NAME1 = 'R Z'
NAME2 = 'Mikhail Tal'
FONT_SIZE = 28
LINE_WIDTH = 4
# let's filter our data
# what we need is only text messages, we do not want to analyze phone calls, music, pictures etc.
to_remove = []
for i, message in enumerate(messages):
    if ('text' not in message
            or not isinstance(message['text'], str)
            or message['text'] == ""
            or message['from'] not in [NAME1, NAME2]
            or message['text_entities'][0]['type'] != 'plain'
            or 'forwarded_from' in message.keys()):
        to_remove.append(i)
messages = messages.drop(labels=to_remove)

# let's get a time range
first_time = messages[0]['date']
last_time = messages.iloc[-1]['date']
print("Range is from ", first_time, " to ", last_time)

# let's get most talkative chatter
rz_counter = 0
mt_counter = 0
for message in messages:
    if message['from'] == NAME1:
        rz_counter += 1
    else:
        mt_counter += 1
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('qtcairo')
plt.figure(figsize=(24, 8))
plt.pie([rz_counter, mt_counter], colors=['lightgreen', 'mediumpurple'], autopct='%1.1f%%', textprops={'fontsize': FONT_SIZE})
plt.legend([NAME1, NAME2], bbox_to_anchor=(-0.1, 0.5), fontsize=FONT_SIZE)
plt.savefig('pie_chart.png')
plt.clf()

# monthly graph of chatters
months = {}

for message in messages:
    if message['date'][:7] not in months:
        months[message['date'][:7]] = {
            'all': 0,
            NAME1: 0,
            NAME2: 0
        }
    months[message['date'][:7]]['all'] += 1
    if message['from'] == NAME1:
        months[message['date'][:7]][NAME1] += 1
    else:
        months[message['date'][:7]][NAME2] += 1
plt.xticks(rotation=90)
plt.plot(months.keys(), [months[key]['all'] for key in months.keys()], linewidth=LINE_WIDTH)
plt.savefig('chat_per_month.png')
plt.clf()

# percentages by month
monthly_percentages = [months[key][NAME1] / months[key]['all'] for key in months.keys()]
plt.fill_between(months.keys(), monthly_percentages, color='lightgreen', alpha=0.5)
plt.fill_between(months.keys(), monthly_percentages, y2 = 1,color='mediumpurple', alpha=0.5)
plt.xticks(rotation=90)
plt.legend([NAME1, NAME2], loc='upper right', fontsize=FONT_SIZE)
plt.savefig('percentages_by_month.png')
plt.clf()

# gratitude counter
gratitudes_by_month = {}
for message in messages:
    if message['date'][:7] not in gratitudes_by_month:
        gratitudes_by_month[message['date'][:7]] = {
            'all': 0,
            NAME1: 0,
            NAME2: 0
        }
    if ('thank' in message['text']
            or 'thx' in (message['text'])
            or 'спс' in message['text']
            or 'спасиб' in message['text']):
        gratitudes_by_month[message['date'][:7]]['all'] += 1
        if message['from'] == NAME1:
            gratitudes_by_month[message['date'][:7]][NAME1] += 1
        else:
            gratitudes_by_month[message['date'][:7]][NAME2] += 1
plt.fill_between(gratitudes_by_month.keys(), [gratitudes_by_month[key][NAME1] for key in gratitudes_by_month.keys()], color='lightgreen', alpha=0.5)
plt.fill_between(gratitudes_by_month.keys(), [gratitudes_by_month[key][NAME1] for key in gratitudes_by_month.keys()], y2 = [gratitudes_by_month[key]['all'] for key in gratitudes_by_month.keys()], color='mediumpurple', alpha=0.5)
plt.xticks(rotation=90)
plt.legend([NAME1, NAME2], fontsize=FONT_SIZE)
plt.savefig('gratitudes.png')
plt.clf()

# average number of words per message
num_words = {
    NAME1: [],
    NAME2: []
}
for message in messages:
    if message['from'] == NAME1:
        num_words[NAME1].append(len(message['text'].split()))
    else:
        num_words[NAME2].append(len(message['text'].split()))
print("Average number of words per message:")
print("R Z:", np.mean(num_words[NAME1]))
print("Mikhail Tal:", np.mean(num_words[NAME2]))

# number of conversations per month
# messages belong to one conversation if they are on distance of no longer than 20 minutes
conversations_by_month = {}
window_begin = 0
prev_message = messages[0]
for window_end, message in enumerate(messages):
    if int(message['date_unixtime']) - int(prev_message['date_unixtime']) > 1200:
        if message['date'][:7] not in conversations_by_month:
            conversations_by_month[message['date'][:7]] = 0
        if window_end - window_begin > 3:
            conversations_by_month[message['date'][:7]] += 1
            window_begin = window_end
            prev_message = message
plt.plot(conversations_by_month.keys(), conversations_by_month.values(), linewidth=LINE_WIDTH)
plt.xticks(rotation=90)
plt.savefig('conversations_per_month.png')
plt.clf()

# compiling pdf with results
import subprocess

f = open('my_document.tex', 'w')
f.write(f"""
\\documentclass[10pt]{{article}}

\\usepackage{{fontspec}}        % Font management
\\setmainfont{{CMU Serif}}      % Main font
%\\sloppy

%\\usepackage[utf8]{{inputenc}}
%\\usepackage[english]{{babel}}

%\\usepackage[margin=1in]{{geometry}} 
\\usepackage{{graphicx}}
\\title{{Chat statistics}}
\\usepackage{{float}}

\\begin{{document}}

    \\maketitle
    This document contains some statistics on chat between R Z and Mikhail Tal.
    The chat was held from {first_time[:10]} to {last_time[:10]}.
    Filtered data contains {len(messages)} messages.
    
    The first graph shows relative number of messages sent by each chat participant.
    \\begin{{figure}}[H]
        \\includegraphics[width=1.1\\textwidth]{{pie_chart.png}}
    \\end{{figure}}
    
    Here is another graph. It shows number of messages sent by each chat participant per month.
    \\begin{{figure}}[H]
        \\includegraphics[width=1.1\\textwidth]{{chat_per_month.png}}
    \\end{{figure}}
    
    \\newpage
    The graph below shows percentages of messages sent by each chat participant per month.
    \\begin{{figure}}[H]
        \\includegraphics[width=1.1\\textwidth]{{percentages_by_month.png}}
    \\end{{figure}}
    
    Another statistics about participants is an average number of words per message.
    Here are the results: 
    \\begin{{itemize}}
        \\item R Z: {np.mean(num_words[NAME1]):.2f}
        \\item Mikhail Tal: {np.mean(num_words[NAME2]):.2f}
    \\end{{itemize}}
    
    If one participant helps another with something, in most cases it implies gratitude. 
    So it's interesting to see how often that happens.
    We use the following keywords to define gratitude:
    "thank", "thx", "спс", "спасиб".
    If any of that found in a message we assume that the message is an expression of gratitude.
    \\begin{{figure}}[H]
        \\includegraphics[width=1.1\\textwidth]{{gratitudes.png}}
    \\end{{figure}}
    
    \\newpage
    The graph below shows number of conversations per month.
    We define sequence of messages a conversation if the following conditions are met:
    \\begin {{itemize}}
        \\item Contains more than 3 messages
        \\item The distance between two messages is less than 20 minutes
    \\end {{itemize}}
    \\begin{{figure}}[H]
        \\includegraphics[width=1.1\\textwidth]{{conversations_per_month.png}}
    \\end{{figure}}
      
\\end{{document}}
""")
f.close()
def compile_latex(filename):
    subprocess.run(['xelatex', filename])
compile_latex('my_document.tex')