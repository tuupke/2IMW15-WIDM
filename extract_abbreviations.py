f = open('abbreviations.txt', 'r')
w = open('abbreviations_clean.txt', 'w')
state = 0
for line in f:
    if line.startswith("<tr>") and state == 0:
        state = 1
    elif line.startswith("<td") and state == 1:
        state = 2
    elif line.startswith("<p>") and state == 2:
        ab = line[3:-5].strip()
        if ab.find("<") == -1 and ab.find(">") == -1:
            w.write(ab.lower())
            w.write('\n')
    else:
        state = 0
