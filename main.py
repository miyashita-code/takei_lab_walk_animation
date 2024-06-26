import tkinter as tk
from PIL import Image, ImageTk, ImageGrab
import pandas as pd
import numpy as np
import cv2
import io

class JointCalculator:
    """
    A class for calculating joint angles and positions for the walking animation.
    """

    def __init__(self, angle_params=None):
        """
        Initialize the JointCalculator with angle parameters.

        Args:
            angle_params (dict, optional): A dictionary containing angle mapping for each joint.
                If None, default values will be used.
        """
        self.default_params = {
            'Knee': {'signal_min': 0, 'signal_max': 152, 'angle_min': 100, 'angle_max': 170},
            'Foot': {'signal_min': 0, 'signal_max': 150, 'angle_min': 85, 'angle_max': 140},
            'Hip': {'signal_min': 0, 'signal_max': 45, 'angle_min': -15, 'angle_max': 60}
        }
        self.angle_params = angle_params or self.default_params

    @staticmethod
    def linear_interpolation(x, x0, y0, x1, y1):
        """
        Perform linear interpolation between two points.

        Args:
            x (float): The input value to interpolate.
            x0, y0 (float): Coordinates of the first point.
            x1, y1 (float): Coordinates of the second point.

        Returns:
            float: The interpolated value.
        """
        return y0 + (y1 - y0) * (x - x0) / (x1 - x0)

    def convert_to_angle(self, df):
        """
        Convert the input signals in the dataframe to angles.

        Args:
            df (pandas.DataFrame): The input dataframe with joint signals.

        Returns:
            pandas.DataFrame: The dataframe with added angle columns.
        """
        for joint, params in self.angle_params.items():
            df[f'{joint} (Angle)'] = df[f'{joint}'].apply(
                lambda x: self.linear_interpolation(
                    x,
                    params['signal_min'], params['angle_min'],
                    params['signal_max'], params['angle_max']
                )
            )
        return df

    @staticmethod
    def calculate_joint_positions(hip_joint, L1, L2, L3, theta_h, theta_k, theta_f):
        """
        Calculate the positions of knee, ankle, and toe based on joint angles.

        Args:
            hip_joint (numpy.array): The position of the hip joint.
            L1, L2, L3 (float): Lengths of hip-to-knee, knee-to-ankle, and foot.
            theta_h, theta_k, theta_f (float): Angles of hip, knee, and foot.

        Returns:
            tuple: Positions of knee, ankle, toe, and angles of hip, knee, foot.
        """
        hip_angle = -theta_h - 90
        knee_pos = hip_joint + L1 * np.array([np.cos(np.radians(hip_angle)), -np.sin(np.radians(hip_angle))])
        knee_angle = 90 - theta_h - theta_k
        ankle_pos = knee_pos + L2 * np.array([np.cos(np.radians(knee_angle)), -np.sin(np.radians(knee_angle))])
        foot_angle = 270 - theta_h - theta_k + theta_f
        toe_pos = ankle_pos + L3 * np.array([np.cos(np.radians(foot_angle)), -np.sin(np.radians(foot_angle))])
        return knee_pos, ankle_pos, toe_pos, hip_angle, knee_angle, foot_angle

class ImageHandler:
    """
    A class for handling image operations such as resizing.
    """

    @staticmethod
    def resize_image(image_path, length):
        """
        Resize an image while maintaining its aspect ratio.

        Args:
            image_path (str): Path to the image file.
            length (int): Desired length of the longer side of the image.

        Returns:
            PIL.Image: The resized image.
        """
        image = Image.open(image_path)
        width, height = image.size
        aspect_ratio = width / height

        if 'hip' in image_path:
            ratio = 0.72
        elif 'knee' in image_path:
            ratio = 0.81
        elif 'foot' in image_path:
            ratio = 0.55
        else:
            ratio = 0.8

        if width > height:
            new_width = length / ratio
            new_height = new_width / aspect_ratio
        else:
            new_height = length / ratio
            new_width = new_height * aspect_ratio
        
        return image.resize((int(new_width), int(new_height)), Image.LANCZOS)

class AnimationCanvas:
    """
    A class for managing the Tkinter canvas and drawing operations.
    """

    def __init__(self, root, width, height, bg_color='white', joint_color='black', bone_color='blue', bone_width=2, show_grid=True):
        """
        Initialize the AnimationCanvas.

        Args:
            root (tk.Tk): The root Tkinter window.
            width (int): Width of the canvas.
            height (int): Height of the canvas.
            bg_color (str): Background color of the canvas.
            joint_color (str): Color of the joint markers.
            bone_color (str): Color of the bones (lines connecting joints).
            bone_width (int): Thickness of the bone lines.
            show_grid (bool): Whether to display a grid in the background.
        """
        self.canvas = tk.Canvas(root, width=width, height=height, bg=bg_color)
        self.canvas.pack()
        self.joint_color = joint_color
        self.bone_color = bone_color
        self.bone_width = bone_width
        self.show_grid = show_grid

    def draw_grid(self, width, height, interval):
        """
        Draw a grid on the canvas.

        Args:
            width (int): Width of the grid.
            height (int): Height of the grid.
            interval (int): Spacing between grid lines.
        """
        if self.show_grid:
            for i in range(0, width, interval):
                self.canvas.create_line(i, 0, i, height, fill='lightgray')
            for i in range(0, height, interval):
                self.canvas.create_line(0, i, width, i, fill='lightgray')

    def display_image(self, image, position, angle):
        """
        Display a rotated image on the canvas.

        Args:
            image (PIL.Image): The image to display.
            position (tuple): The (x, y) position to place the image.
            angle (float): The rotation angle in degrees.

        Returns:
            ImageTk.PhotoImage: The displayed image object.
        """
        rotated_image = image.rotate(angle, expand=True)
        tk_image = ImageTk.PhotoImage(rotated_image)
        x, y = position
        self.canvas.create_image(x, y, image=tk_image)
        return tk_image

    def draw_joints_and_bones(self, hip_joint, knee_pos, ankle_pos, toe_pos):
        """
        Draw joints as circles and bones as lines on the canvas.

        Args:
            hip_joint, knee_pos, ankle_pos, toe_pos (numpy.array): Joint positions.
        """
        joints = [hip_joint, knee_pos, ankle_pos, toe_pos]
        for joint in joints:
            self.canvas.create_oval(joint[0]-5, joint[1]-5, joint[0]+5, joint[1]+5, fill=self.joint_color)

        self.canvas.create_line(hip_joint[0], hip_joint[1], knee_pos[0], knee_pos[1], fill=self.bone_color, width=self.bone_width)
        self.canvas.create_line(knee_pos[0], knee_pos[1], ankle_pos[0], ankle_pos[1], fill=self.bone_color, width=self.bone_width)
        self.canvas.create_line(ankle_pos[0], ankle_pos[1], toe_pos[0], toe_pos[1], fill=self.bone_color, width=self.bone_width)

class WalkingAnimation:
    """
    Main class for controlling the walking animation.
    """

    def __init__(self, csv_file, output_file, angle_params=None, bone_lengths=None, hip_position=None,
                 bg_color='white', joint_color='black', bone_color='blue', bone_width=2, show_grid=True):
        """
        Initialize the WalkingAnimation.

        Args:
            csv_file (str): Name of the CSV file containing animation data.
            output_file (str): Name of the output video file.
            angle_params (dict, optional): Custom angle parameters for joints.
            bone_lengths (dict, optional): Custom bone lengths.
            hip_position (tuple, optional): Custom initial hip position.
            bg_color (str): Background color of the animation.
            joint_color (str): Color of the joint markers.
            bone_color (str): Color of the bones.
            bone_width (int): Thickness of the bone lines.
            show_grid (bool): Whether to display a grid in the background.
        """
        self.joint_calculator = JointCalculator(angle_params)
        
        self.df = pd.read_csv(f"inputs/{csv_file}")
        self.df = self.joint_calculator.convert_to_angle(self.df)
        
        self.bone_lengths = bone_lengths or {'L1': 250, 'L2': 300, 'L3': 90}
        self.hip_joint = np.array(hip_position or [350, 100])

        self.root = tk.Tk()
        self.canvas = AnimationCanvas(self.root, 1000, 1000, bg_color, joint_color, bone_color, bone_width, show_grid)
        
        self.hip_image = ImageHandler.resize_image('assets/hip_image.png', self.bone_lengths['L1'])
        self.knee_image = ImageHandler.resize_image('assets/knee_image.png', self.bone_lengths['L2'])
        self.foot_image = ImageHandler.resize_image('assets/foot_image.png', self.bone_lengths['L3'])

        self.global_hip_image = None
        self.global_knee_image = None
        self.global_foot_image = None

        self.frame_rate = 10
        self.total_frames = len(self.df)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.out = cv2.VideoWriter(f"output/{output_file}", fourcc, 10.0, (1000, 1000))

    def animate(self, frame, is_show_born_joint=False):
        """
        Perform animation for a single frame.

        Args:
            frame (int): The current frame number.
            is_show_born_joint (bool): Whether to show joints and bones.
        """
        if frame >= self.total_frames:
            self.out.release()
            self.root.destroy()
            return

        self.canvas.canvas.delete("all")
        self.canvas.draw_grid(1000, 1000, 50)

        theta_h = self.df['Hip (Angle)'].iloc[frame]
        theta_k = self.df['Knee (Angle)'].iloc[frame]
        theta_f = self.df['Foot (Angle)'].iloc[frame]

        knee_pos, ankle_pos, toe_pos, hip_angle, knee_angle, foot_angle = self.joint_calculator.calculate_joint_positions(
            self.hip_joint, self.bone_lengths['L1'], self.bone_lengths['L2'], self.bone_lengths['L3'],
            theta_h, theta_k, theta_f)

        hip_center = (self.hip_joint + knee_pos) / 2
        knee_center = (knee_pos + ankle_pos) / 2
        foot_center = (ankle_pos + toe_pos) / 2

        self.global_hip_image = self.canvas.display_image(self.hip_image, hip_center, hip_angle)
        self.global_knee_image = self.canvas.display_image(self.knee_image, knee_center, knee_angle)
        self.global_foot_image = self.canvas.display_image(self.foot_image, foot_center, foot_angle)

        if is_show_born_joint:
            self.canvas.draw_joints_and_bones(self.hip_joint, knee_pos, ankle_pos, toe_pos)

        self.canvas.canvas.update()
        x = self.canvas.canvas.winfo_rootx()
        y = self.canvas.canvas.winfo_rooty()
        x1 = x + self.canvas.canvas.winfo_width()
        y1 = y + self.canvas.canvas.winfo_height()
        img = ImageGrab.grab(bbox=(x, y, x1, y1))
        img = img.resize((1000, 1000), Image.LANCZOS)
        img = np.array(img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        self.out.write(img)

        self.root.after(int(1000 / self.frame_rate), self.animate, frame + 1, is_show_born_joint)

    def run(self, is_show_born_joint=False):
        """
        Start the animation.

        Args:
            is_show_born_joint (bool): Whether to show joints and bones.
        """
        try:
            self.animate(0, is_show_born_joint)
            self.root.mainloop()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.out.release()
            self.root.destroy()

if __name__ == "__main__":
    custom_angle_params = {
        'Knee': {'signal_min': 0, 'signal_max': 152, 'angle_min': 100, 'angle_max': 170},
        'Foot': {'signal_min': 0, 'signal_max': 150, 'angle_min': 85, 'angle_max': 140},
        'Hip': {'signal_min': 0, 'signal_max': 45, 'angle_min': -15, 'angle_max': 60}
    }
    custom_bone_lengths = {'L1': 250, 'L2': 300, 'L3': 90}
    custom_hip_position = (400, 100)

    animation = WalkingAnimation('data.csv', 'output.mp4',
                                 angle_params=custom_angle_params,
                                 bone_lengths=custom_bone_lengths,
                                 hip_position=custom_hip_position,
                                 bg_color='white',
                                 joint_color='black',
                                 bone_color='blue',
                                 bone_width=2,
                                 show_grid=True)

    animation.run(is_show_born_joint=True)