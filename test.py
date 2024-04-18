import os

folder_path = 'D:/CN_Ass/input/book/'

for filename in os.listdir(folder_path):
  filepath = os.path.join(folder_path, filename)
  print(filename[0])