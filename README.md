# Walking Animation Project

This project generates a walking animation based on CSV data input. Follow these steps to set up and run the animation.

## Prerequisites

- Python 3.9.13
- Git
- Visual Studio Code (recommended)

## Setup

1. Open a terminal and create a new directory:
   ```
   mkdir your_project_name
   cd your_project_name
   ```

2. Clone the repository:
   ```
   git clone https://github.com/miyashita-code/takei_lab_walk_animation.git
   cd takei_lab_walk_animation
   ```

3. Ensure you have Python 3.9.13 installed. You can download it from the official Python website if needed.

4. Create a virtual environment with Python 3.9.13:
   ```
   py -3.9 -m venv .venv
   ```
   Note: If `python3.9` doesn't work, try `py -3.9` on Windows or the full path to your Python 3.9.13 executable.

5. Activate the virtual environment:
   - On Windows (PowerShell):
     ```
     .\.venv\Scripts\Activate.ps1
     ```
   - On macOS and Linux:
     ```
     source .venv/bin/activate
     ```

6. Verify that you're using Python 3.9.13:
   ```
   python --version
   ```
   This should output "Python 3.9.13".

7. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Input Data

1. Place your CSV file in the `inputs` folder.
2. Ensure your CSV file structure matches the sample:

   ```
   Timestamp,Knee,,Foot,,Hip
   0.1,59.08655,,14.63368,,15.98534
   0.2,106.53334,,15.82331,,0
   0.3,57.72622,,83.69337,,8.52444
   0.4,84.73368,,72.66551,,3.48557
   ...
   ```

## Customizing the Animation

Open `main.py` and adjust the following parameters as needed:

```python
# Specify the path to your CSV file here
csv_file_path = 'inputs/your_csv_file.csv'

custom_angle_params = {
    'Knee': {'signal_min': 0, 'signal_max': 152, 'angle_min': 100, 'angle_max': 170},
    'Foot': {'signal_min': 0, 'signal_max': 150, 'angle_min': 85, 'angle_max': 140},
    'Hip': {'signal_min': 0, 'signal_max': 45, 'angle_min': -15, 'angle_max': 60}
}
custom_bone_lengths = {'L1': 250, 'L2': 300, 'L3': 90}
custom_hip_position = (400, 100)

animation = WalkingAnimation(csv_file_path, 'output/custom_output.mp4',
                             angle_params=custom_angle_params,
                             bone_lengths=custom_bone_lengths,
                             hip_position=custom_hip_position,
                             bg_color='white',
                             joint_color='black',
                             bone_color='blue',
                             bone_width=2,
                             show_grid=True)
```

To use your own CSV file:
1. Place your CSV file in the `inputs` folder.
2. Change the `csv_file_path` variable to match your CSV file's name. For example:
   ```python
   csv_file_path = 'inputs/my_walking_data.csv'
   ```
3. Ensure your CSV file follows the required structure as described in the "Input Data" section.

You can also customize the output file name and location by changing the second argument in the `WalkingAnimation` constructor. For example:
```python
animation = WalkingAnimation(csv_file_path, 'output/my_custom_animation.mp4', ...)
```

Remember to adjust other parameters as needed to match your data and desired animation style.

## Detailed Parameter Explanations

* `angle_params`: Defines the mapping between input signals and joint angles.
  - Structure: `{'JointName': {'signal_min': float, 'signal_max': float, 'angle_min': float, 'angle_max': float}}`
  - Default values:
    ```python
    {
        'Knee': {'signal_min': 0, 'signal_max': 152, 'angle_min': 100, 'angle_max': 170},
        'Foot': {'signal_min': 0, 'signal_max': 150, 'angle_min': 85, 'angle_max': 140},
        'Hip': {'signal_min': 0, 'signal_max': 45, 'angle_min': -15, 'angle_max': 60}
    }
    ```
  - Purpose: This maps the input signal range to the corresponding angle range for each joint.
  - Adjustment: Modify these values to change how the input data is interpreted as joint angles. For example, increasing the 'angle_max' for the knee will result in a wider range of knee motion.

* `bone_lengths`: Sets the lengths of different body segments in pixels.
  - Structure: `{'L1': int, 'L2': int, 'L3': int}`
  - Default values: `{'L1': 250, 'L2': 300, 'L3': 90}`
  - L1: Length from hip to knee
  - L2: Length from knee to ankle
  - L3: Length of the foot
  - Purpose: Defines the proportions of the animated figure.
  - Adjustment: Increase or decrease these values to change the relative sizes of body parts. For example, increasing L1 will make the thigh longer.

* `hip_position`: Sets the initial position of the hip joint on the canvas.
  - Structure: `(x: int, y: int)`
  - Default value: `(400, 100)`
  - Purpose: Determines where the figure is placed on the canvas.
  - Adjustment: Modify these values to move the entire figure. Increasing x moves it right, increasing y moves it down.

* `bg_color`: Background color of the animation.
  - Type: string (color name or hexadecimal color code)
  - Default value: `'white'`
  - Purpose: Sets the canvas background color.
  - Adjustment: Change to any valid color name (e.g., 'black', 'lightblue') or hex code (e.g., '#RRGGBB').

* `joint_color`: Color of the joint markers.
  - Type: string (color name or hexadecimal color code)
  - Default value: `'black'`
  - Purpose: Determines the color of the circles representing joints.
  - Adjustment: Change to make joints more or less visible against the background.

* `bone_color`: Color of the bones (lines connecting joints).
  - Type: string (color name or hexadecimal color code)
  - Default value: `'blue'`
  - Purpose: Sets the color of the lines representing bones.
  - Adjustment: Change to alter the appearance of the figure's structure.

* `bone_width`: Thickness of the bone lines.
  - Type: int
  - Default value: `2`
  - Purpose: Determines how thick the lines representing bones appear.
  - Adjustment: Increase for more visible bones, decrease for a more subtle appearance.

* `show_grid`: Whether to display a grid in the background.
  - Type: boolean
  - Default value: `True`
  - Purpose: Toggles the visibility of the background grid.
  - Adjustment: Set to `False` to remove the grid, useful for cleaner output or when the grid interferes with visibility.

When adjusting these parameters, keep in mind:
1. Color combinations: Ensure that your chosen colors for joints, bones, and background provide sufficient contrast for visibility.
2. Proportions: When changing bone lengths, try to maintain realistic body proportions for a natural-looking animation.
3. Canvas size: The default canvas size is 1000x1000 pixels. If you change the hip position or bone lengths significantly, ensure the figure still fits within the canvas.
4. Performance: Very large values for bone width or complex color settings might affect performance on slower systems.

## Running the Animation

1. Run the script:
   ```
   python main.py
   ```

2. The output MP4 file will be generated in the `output` folder.

## Deactivating the Virtual Environment

After you're done, deactivate the virtual environment:
```
deactivate
```

## Troubleshooting

If you encounter any issues, ensure:
- You're using Python 3.9.13 in your virtual environment
- All required packages are installed correctly
- Your input CSV file is in the correct format and location
- You have write permissions in the output directory

Common issues and solutions:
1. **ImportError**: Make sure all required packages are installed (`pip install -r requirements.txt`).
2. **FileNotFoundError**: Check that your CSV file is in the correct location and named correctly.
3. **PermissionError**: Ensure you have write permissions in the output directory.
4. **RuntimeError from Tkinter**: This might occur if you're running the script in a non-GUI environment. Ensure you're running it on a system with a graphical interface.

For further assistance, please open an issue on the GitHub repository.

## Contributing

Contributions to this project are welcome. Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License - see the LICENSE file for details.