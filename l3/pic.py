import csv
with open('lvn.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    base = 0
    dce = 0
    lvn = 0
    for i, row in enumerate(reader):
        # skip first line
        curr_bench = ""
        data = row[0].split(",")
        if i != 0:
          curr_bench = data[0]
          run = data[1]
          instrs = int(data[2])
          if run == "baseline":
            base = instrs
          elif run == "dce":
            dce = instrs
          elif run == "lvn_dce":
            lvn = instrs
            dce_per = ((base - dce) / base) * 100
            lvn_per = ((base - lvn) / base) * 100
            print(f'bench: ', {curr_bench})
            print(f'dce: {dce_per:9.2f}')
            print(f'lvn: {lvn_per:9.2f}')