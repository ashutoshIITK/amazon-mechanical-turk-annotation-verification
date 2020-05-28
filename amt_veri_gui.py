import PySimpleGUI as sg
import os
from PIL import Image
import pandas as pd

# Simple Image Browser based on PySimpleGUI

w, h = sg.Window.get_screen_size()

df_name = "Batch_4052999_batch_results.csv"

annotations_results = pd.read_csv(f"data/{df_name}")

saved_df_name = df_name.split(".")[0] + "_completed.csv"

# Get the folder containing the images from the user
folder = sg.PopupGetFolder('AMT Annotation Verification for Bounding Boxes', 'Image folder to open', default_path='/home/ubuntu/Desktop/FY2020/MastersResearch/amazon-mechanical-turk-annotation-verification/output/third')

# get list of PNG files in folder
png_files = [folder + '/' + f for f in os.listdir(folder) if '.png' in f]
filenames_only = [f for f in os.listdir(folder) if '.png' in f]

if len(png_files) == 0:
    sg.MsgBox('No PNG images in folder')
    exit(0)

# create the form that also returns keyboard events
form = sg.FlexForm("AMT Annotation Verification for Bounding Boxes", return_keyboard_events=True, location=(0,0), size=(w, h), resizable=True, use_default_focus=False )

# make these 2 elements outside the layout because want to "update" them later
# initialize to the first PNG file in the list
image_elem = sg.Image(filename=png_files[0],size=(w, h))
filename_display_elem = sg.Text(png_files[0], size=(80, 3))
file_num_display_elem = sg.Text('File 1 of {}'.format(len(png_files)), size=(20,1))
addtional_info = sg.Text('Working Time:{}, Approval Rate: {}'.format(1,2), size=(25,2))
filename = png_files[0]
# define layout, show and read the form
col = [[filename_display_elem],
          [image_elem],
          [sg.ReadFormButton('Next', size=(8,2)), sg.ReadFormButton('Prev', size=(8,2)),  sg.ReadFormButton('Approve', size=(8,2)), 
          sg.ReadFormButton('Reject', size=(8,2)), sg.ReadFormButton('Save Work', size=(8,2)), addtional_info, file_num_display_elem]]

col_files = [[sg.Listbox(values=filenames_only, size=(60,30), key='listbox')],
             [sg.ReadFormButton('Read')]]
layout = [[sg.Column(col_files), sg.Column(col)]]

# DeprecationWarning: LayoutAndRead is no longer supported... change your call window.Layout(layout).Read()
button, values = form.Layout(layout).Read()          # Shows form on screen

# loop reading the user input and displaying image, filename
i = 0
flag = True
while True:

    # perform button and keyboard operations

    if button is None:
        break
    elif button in ('Next', 'MouseWheel:Down', 'Down:40', 'Next:34') and i < len(png_files)-1:
        i += 1
    elif button in ('Prev', 'MouseWheel:Up', 'Up:38', 'Prior:33') and i > 0:
        i -= 1

    elif button in ('Approve', 'MouseWheel:Down', 'Down:40', 'Next:34') and i < len(png_files)-1:
        annotations_results.loc[annotations_results["Input.image_url"] == f"https://mturk-dataset.s3-ap-northeast-1.amazonaws.com/ash/{filename.split('@')[-1][:-3]}jpg", "Approve"] = "x"
        i += 1
        print('You have approved this annotation!')
    elif button in  ("Reject",'MouseWheel:Down', 'Down:40', 'Next:34') and i < len(png_files)-1:
        annotations_results.loc[annotations_results["Input.image_url"] == f"https://mturk-dataset.s3-ap-northeast-1.amazonaws.com/ash/{filename.split('@')[-1][:-3]}jpg", "Reject"] = "poor quality"
        i += 1
        print("You have rejected this annotation.")
    elif button == "Save Work":
        annotations_results.to_csv(saved_df_name, index = False)
        print("Saving Dataframe to CSV.")


    if button == 'Read':
        filename = folder + '/' + values['listbox'][0]
        # print(filename)
    else:
        filename = png_files[i]

    # update window with new image
    image_elem.Update(filename=filename)
    # update window with filename
    filename_display_elem.Update("filename")
    # update page display
    file_num_display_elem.Update('File {} of {}'.format(i+1, len(png_files)))

    # Upadte the worker time value
    addtional_info.Update('Worker Time: {} \nApproval Rate: {}'.format(filename.split('/')[-1].split("@")[0],
        filename.split('/')[-1].split("@")[1]))


    # read the form
    button, values = form.Read()
