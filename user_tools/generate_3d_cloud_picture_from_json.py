import json
import os
import sys
from PIL import Image

print("This is a conversion tool which generates three .jpg files from .json 3-dimension dot data files.")
print("Please make sure that:")
print("1. All the files in the folder have been backuped.")
print("2. All the dot data file are in json format and have the following file structure:")
print('{\n    "min_coordinate":[min_x,min_y,min_z],\
      \n    "max_coordinate":[max_x,max_y,max_z],\
      \n    "dots":[\
      \n        [x_1,y_1,z_1],\
      \n        [x_2,y_2,z_2],\
      \n        ...\
      \n        [x_n,y_n,z_n]\
      \n    ],\
      \n    "pixels":[pixel_x,pixel_y,pixel_z]\
      \n}')
print("Where all the points are in the cuboid formed by (min_x,min_y,min_z),(max_x,max_y,max_z) and the pixels generated on each dimension are given by the param 'pixels'.")
print("The tool will replace all the json file in the subfolder into three correspoding image. The name.json will be replaced by name_1.jpg,name_2.jpg and name_3.jpg.")
print("---------------------------------------------------")
if len(sys.argv)!=2:    
    print("Usage: <script_name> <target_directory>")
    exit(0)
os.system("pause")

for root, dirs, files in os.walk(sys.argv[1]):
    for file in files:
        if file.endswith('.json'):
            file_path=os.path.join(root,file)
            print("Verifying "+file_path+" ...")
            with open(file_path, 'r') as f:
                try:
                    json_data = json.load(f)
                except ValueError as e:
                    print(f"Error: {file_path} does not contain valid JSON.")
                    exit(0)

            if not isinstance(json_data, dict):
                print(f"Error: {file_path} does not contain a dictionary.")
                exit(0)

            required_keys = {"min_coordinate", "max_coordinate", "dots"}
            if not required_keys.issubset(json_data.keys()):
                missing_keys = required_keys - set(json_data.keys())
                print(f"Error: {file_path} is missing the following keys: {missing_keys}.")
                exit(0)

            min_coord = json_data.get("min_coordinate")
            max_coord = json_data.get("max_coordinate")
            dots = json_data.get("dots")
            pixels = json_data.get("pixels")

            if not isinstance(min_coord, list) or len(min_coord) != 3 or not all(isinstance(x, (int, float)) for x in min_coord):
                print(f"Error: {file_path} has an invalid 'min_coordinate'.")
                exit(0)

            if not isinstance(max_coord, list) or len(max_coord) != 3 or not all(isinstance(x, (int, float)) for x in max_coord):
                print(f"Error: {file_path} has an invalid 'max_coordinate'.")
                exit(0)
            
            if not isinstance(pixels, list) or len(pixels) != 3 or not all(isinstance(x, int) for x in max_coord):
                print(f"Error: {file_path} has an invalid 'pixels'.")
                exit(0)

            if not isinstance(dots, list) or not all(isinstance(x, list) and len(x) == 3 and all(isinstance(y, (int, float)) for y in x) for x in dots):
                print(f"Error: {file_path} has invalid 'dots'.")
                exit(0)
            
            if not all(min_coord[i]<=max_coord[i] for i in range(3)):
                print(f"Error: {file_path} is wrong: mincoord large than maxcoord.")
                exit(0)
            
            if not all(all(dot[i]>=min_coord[i] and dot[i]<=max_coord[i] for i in range(3)) for dot in dots):
                print(f"Error: {file_path} is wrong: dots not in range")
                exit(0)

for root, dirs, files in os.walk(sys.argv[1]):
    for file in files:
        if file.endswith('.json'):
            print("Generating "+os.path.join(root,file)+" ...")
            data = json.load(open(os.path.join(root,file)))
            min_coord = json_data.get("min_coordinate")
            max_coord = json_data.get("max_coordinate")
            dots = json_data.get("dots")
            pixels = json_data.get("pixels")
            for i in range(3):
                image_size=[]
                for j in range(3):
                    if j!=i:
                        image_size.append(pixels[j])
                image_pixels = [(0, 0, 0) for _ in range(image_size[0] * image_size[1])]
                for d in dots:
                    coord=[]
                    for j in range(3):
                        if j!=i:
                            coord.append((d[j]-min_coord[j])/(max_coord[j]-min_coord[j]))
                    for j in range(2):
                        coord[j]=round(coord[j]*image_size[j])
                    image_pixels[coord[0]*image_size[1]+coord[1]]=(115, 252, 40)
                image = Image.new("RGB", (image_size[0], image_size[1]))
                image.putdata(image_pixels)
                image.save(os.path.join(root,file.replace(".json",f"_{i+1}.jpg")))

for root, dirs, files in os.walk(sys.argv[1]):
    for file in files:
        if file.endswith('.json'):
            os.remove(os.path.join(root,file))