bl_info = {
    "name": "Blender Mocap",
    "author": "Daniel W",
    "version": (0, 1),
    "blender": (3, 60, 0),
    "location": "3D View > Sidebar > Blender Mocap",
    "description": "Motion capture",
    "category": "3D View"
}


import bpy
from bpy.types import Panel, Operator, PropertyGroup, FloatProperty, PointerProperty, StringProperty
from bpy.utils import register_class, unregister_class
from bpy_extras.io_utils import ImportHelper
import bpy_extras


body_names = [
"00 nose",
"01 left eye (inner)",
"02 left eye",
"03 left eye (outer)",
"04 right eye (inner)",
"05 right eye",
"06 right eye (outer)",
"07 left ear",
"08 right ear",
"09 mouth (left)",
"10 mouth (right)",
"11 left shoulder",
"12 right shoulder",
"13 left elbow",
"14 right elbow",
"15 left wrist",
"16 right wrist",
"17 left pinky",
"18 right pinky",
"19 left index",
"20 right index",
"21 left thumb",
"22 right thumb",
"23 left hip",
"24 right hip",
"25 left knee",
"26 right knee",
"27 left ankle",
"28 right ankle",
"29 left heel",
"30 right heel",
"31 left foot index",
"32 right foot index",
]



def full_setup():
    """ Setup tracking boxes for body, face and hand tracking """
    scene_objects = [n for n in bpy.context.scene.objects.keys()]
    pose = bpy.context.scene.objects["Pose"]
    
    context = bpy.context
    scene = context.scene
    mytool = scene.settings

#    if "Hand Left" not in scene_objects:
 #       bpy.ops.object.add(radius=1.0, type='EMPTY')
  #      hand_left = bpy.context.active_object
   #     hand_left.name = "Hand Left"
    #    hand_left.parent = pose

#        for k in range(21):
 #           bpy.ops.mesh.primitive_cube_add()
  #          box = bpy.context.active_object
   #         box.name = str(k).zfill(2) + "Hand Left"
    #        box.scale = (0.01, 0.01, 0.01)
     #       box.parent = hand_left

#    if "Hand Right" not in scene_objects:
 #       bpy.ops.object.add(radius=1.0, type='EMPTY')
  #      hand_right = bpy.context.active_object
   #     hand_right.name = "Hand Right"
    #    hand_right.parent = pose

#        for k in range(21):
 #           bpy.ops.mesh.primitive_cube_add()
  #          box = bpy.context.active_object
   #         box.name = str(k).zfill(2) + "Hand Right"
    #        box.scale = (0.01, 0.01, 0.01)
     #       box.parent = hand_right

    if "Face" not in scene_objects:
        bpy.ops.object.add(radius=1.0, type='EMPTY')
        face = bpy.context.active_object
        face.name = "Face"
        face.parent = pose
        
        clc = face.constraints.new("COPY_LOCATION")
        object = scene.objects.get("23 left hip")
        clc.target = object
        
        face_names = [
        "013Face",
        "014Face",
        "078Face",
        "308Face",
        "419Face",
        "196Face"
        ]
        
        for n in range(6):
            bpy.ops.mesh.primitive_cube_add()
            box = bpy.context.active_object
            box.name = face_names[n]
            box.scale = (0.002, 0.002, 0.002)
            box.parent = face
            

#    hand_left = bpy.context.scene.objects["Hand Left"]
 #   hand_right = bpy.context.scene.objects["Hand Right"]
    face = bpy.context.scene.objects["Face"]
    #return hand_left, hand_right, face
    return face



# The bones that normally stretch to fit the drivers' locations
stretch_bones_influence = [
"DEF-shin.L",
"DEF-shin.R",
"DEF-shin.L.001",
"DEF-shin.R.001",
"DEF-foot.L",
"DEF-foot.R",
"DEF-thigh.L.001",
"DEF-thigh.R.001",
"DEF-thigh.R",
"DEF-thigh.L",
"DEF-upper_arm.L",
"DEF-upper_arm.R",
"DEF-upper_arm.L.001",
"DEF-upper_arm.R.001",
"DEF-forearm.L",
"DEF-forearm.R",
"DEF-forearm.L.001",
"DEF-forearm.R.001"
]



#407 and 183 = lips.R and lips.L
#013 and 014 = lip.T and lip.B
#088 = lip.B.L.001
#318 = lip.B.R.001
#310 = lip.T.R.001
#080 = lip.T.L.001
#152 = chin
#145 = lid.B.L.002
#159 = lid.T.L.002
#374 = lid.B.R.002
#386 = lid.T.R.002
#027 = brow.T.L.002
#257 = brow.T.R.002
#030 = brow.T.L.001
#260 = brow.T.R.001
#286 = brow.T.R.003
#056 = brow.T.L.003
#207 = cheek.B.L.001
#427 = cheek.B.R.001
#129 = nose.L.001
#358 = nose.R.001
#019 = nose.002

stretch_bones_ik = [
"MCH-shin_ik.L",
"MCH-shin_ik.R",
"MCH-forearm_ik.L",
"MCH-forearm_ik.R"

]

def delete_stretch():
    context = bpy.context
    scene = context.scene  
    mytool = scene.settings
    current_armature = (mytool.eyedropper)
    new_armature = bpy.data.objects[current_armature]
    for n in range(17):
        new_armature.pose.bones[stretch_bones_influence[n]].constraints["Stretch To"].influence = 0
    for k in range(4):
        new_armature.pose.bones[stretch_bones_ik[k]].constraints["IK"].use_stretch = False
        new_armature.pose.bones[stretch_bones_ik[k]].constraints["IK.001"].use_stretch = False
        
        
        

import numpy as np
import math


def run_full(file_path):
    try:
        import cv2
        import mediapipe as mp
    except Exception as e:
        # bpy.ops.message.messagebox('INVOKE_DEFAULT', message = 'Installing additional libraries, this may take a moment...')
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        #install()
        import cv2
        import mediapipe as mp
        
    delete_stretch()

    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    body = body_setup()
    face = full_setup()
    #hand_left, hand_right, face = full_setup()

    context = bpy.context
    scene = context.scene  

    mp_drawing = mp.solutions.drawing_utils
    mp_holistic = mp.solutions.holistic

    if file_path == "None": cap = cv2.VideoCapture(0)
    else: cap = cv2.VideoCapture(file_path)

    with mp_holistic.Holistic(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as holistic:

        for n in range(9000):
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            # image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = holistic.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            xl = bpy.data.scenes[0].frame_current
            
            Pose = bpy.data.objects["Pose"]

            if results.pose_landmarks:
                bns = [b for b in results.pose_landmarks.landmark]
                scale = 2
                bones = sorted(body.children, key=lambda b: b.name)

                for k in range(33):
                    bones[k].location.y = ((bns[k].z)*0.5)
                    bones[k].location.x = ((0.5-bns[k].x)*scale) 
                    bones[k].location.z = ((0.5-bns[k].y)*scale)
                    bones[k].keyframe_insert(data_path="location", frame=xl)
                    
                    
                    
                    
                head_1 = bpy.context.scene.objects["01 left eye (inner)"]
                head_2 = bpy.context.scene.objects["00 nose"]
                r_hand_1 = bpy.context.scene.objects["16 right wrist"]
                r_hand_2 = bpy.context.scene.objects["20 right index"]
                l_hand_1 = bpy.context.scene.objects["15 left wrist"]
                l_hand_2 = bpy.context.scene.objects["19 left index"]
                hip_1 = bpy.context.scene.objects["24 right hip"]
                hip_2 = bpy.context.scene.objects["23 left hip"]
                shoulder_1 = bpy.context.scene.objects["12 right shoulder"]
                shoulder_2 = bpy.context.scene.objects["11 left shoulder"]
                foot_r = bpy.context.scene.objects["31 left foot index"]
                foot_l = bpy.context.scene.objects["32 right foot index"]
                r_shoulder = bpy.context.scene.objects["11 left shoulder"]
                l_shoulder = bpy.context.scene.objects["12 right shoulder"]
                r_thumb = bpy.context.scene.objects["21 left thumb"]
                l_thumb = bpy.context.scene.objects["22 right thumb"]

                    
                xl = bpy.data.scenes[0].frame_current
                l_xl = xl - 1
                head_rot_initial = 0
                r_hand_rot_initial = 0
                l_hand_rot_initial = 0
                hip_rot_initial = 0
                
                
                context = bpy.context
                scene = context.scene  
                mytool = scene.settings
                
                scale_i = 1
                loc_i = 0
                bend_dis_i = 0.5
                
                if l_xl < xl:
                    hip_rot_z = hip_1.location.x - hip_2.location.x
                    scale = abs(((hip_1.location.y * 15) * (hip_rot_z)))
                    scale_f = scale_i - scale
                    scale_d = 1 / scale_f
                    Pose.scale = (scale_d, scale_d, scale_d)
                    Pose.keyframe_insert(data_path="scale", frame = xl)
                    scale_i = scale
                    
                    bend_dis = r_shoulder.location.z - hip_2.location.z
                    bend_dis_f = bend_dis_i - bend_dis
                    bend = np.arcsin(bend_dis_f) * 2 * hip_1.location.y * 30
                    hip_1.rotation_euler = (0, bend, 0)
                    hip_1.keyframe_insert(data_path="rotation_euler", frame = xl)
                    bend_dis_i = bend_dis
                    
                    
                    
                if l_xl < xl:
                    head_rot_x = head_1.location.x - head_2.location.x
                    head_rot_z = head_1.location.z - head_2.location.z
                    head_rot = (np.arctan([head_rot_x / head_rot_z])) + 0.15
                    head_rot_final = head_rot - head_rot_initial
                    head_2.rotation_euler = (90, (head_rot_final), 0)
                    head_2.keyframe_insert(data_path="rotation_euler", frame = xl)
                    head_rot_initial = head_rot
                    
                            

#                if l_xl < xl:
 #                   r_hand_rot_x = r_hand_1.location.x - r_hand_2.location.x
  #                  r_hand_rot_z = r_hand_1.location.z - r_hand_2.location.z
   #                 r_arm_z = r_shoulder.location.z - r_thumb.location.z
    #                    
     #               if r_hand_rot_z == 0:
      #                  r_hand_rot_z = r_hand_rot_z + 0.0001
       #                     
        #            else:
         #           #if r_arm_z < 0.25:
          #              r_hand_rot = (np.arctan([r_hand_rot_x / r_hand_rot_z]))
           #             r_hand_rot_final = r_hand_rot - r_hand_rot_initial
            #            r_hand_2.rotation_euler = (180, -r_hand_rot_final, -180)
             #           r_hand_2.keyframe_insert(data_path="rotation_euler", frame = xl)
              #          r_hand_rot_initial = r_hand_rot
                        #else:
                         #   r_hand_rot = (np.arctan([r_hand_rot_x / r_hand_rot_z]))
                          #  r_hand_rot_final = r_hand_rot - r_hand_rot_initial
                           # r_hand_2.rotation_euler = (-90, r_hand_rot_final, 180)
                            #r_hand_2.keyframe_insert(data_path="rotation_euler", frame = xl)
                            #r_hand_rot_initial = r_hand_rot
                        
                    
                    
                            
#                if l_xl < xl:
 #                   l_hand_rot_x = l_hand_1.location.x - l_hand_2.location.x
  #                  l_hand_rot_z = l_hand_1.location.z - l_hand_2.location.z
   #                 l_arm_z = l_shoulder.location.z - l_thumb.location.z
    #                    
     #               if l_hand_rot_z == 0:
      #                  l_hand_rot_z = l_hand_rot_z + 0.0001
       #                     
        #            else:
         #           #if l_arm_z < 0.25:
          #              l_hand_rot = (np.arctan([l_hand_rot_x / l_hand_rot_z]))
           #             l_hand_rot_final = l_hand_rot - l_hand_rot_initial
            #            l_hand_2.rotation_euler = (180, -l_hand_rot_final, 180)
             #           l_hand_2.keyframe_insert(data_path="rotation_euler", frame = xl)
              #          l_hand_rot_initial = l_hand_rot
        #                else:
         #                   l_hand_rot = (np.arctan([l_hand_rot_x / l_hand_rot_z]))
          #                  l_hand_rot_final = l_hand_rot - l_hand_rot_initial
           #                 l_hand_2.rotation_euler = (-90, l_hand_rot_final, 180)
            #                l_hand_2.keyframe_insert(data_path="rotation_euler", frame = xl)
             #               l_hand_rot_initial = l_hand_rot
             
             
                hip_rotation_initial = 0
                
                if l_xl < xl:
                    hip_rotation_y = hip_1.location.y  - hip_2.location.y
                    
                    hip_rotation_z = np.arcsin(hip_rotation_y) * (180 / 3.14) / 5
                    
                    hip_rot = (hip_rotation_z)
                    hip_rot_final = hip_rot - hip_rot_initial
                    hip_2.rotation_euler = (0, 0, hip_rot_final)
                    hip_2.keyframe_insert(data_path="rotation_euler", frame = xl)
                    hip_rot_initial = hip_rot
                            
                if l_xl < xl:
                    hip_rot_z = hip_1.location.x - hip_2.location.x
                    torso_width = hip_rot_z
                    torso_height = shoulder_1.location.z - hip_1.location.z
                    area = ((abs(torso_width * torso_height))*10)
                        
                    if (shoulder_1.location.y - shoulder_2.location.y) == 0:
                        shoulder_1.location.y = shoulder_1.location.y + 0.001
                            
                    torso_slope = -(((shoulder_1.location.z + 10) - shoulder_2.location.z) / (shoulder_1.location.y - shoulder_2.location.y))
                        
                    depth_value_initial = 0
                        
                    if torso_width == 0.00:
                        torso_width = torso_width + 0.001
                        
                    if (torso_width * 1.4) > torso_height:
                        depth_value = torso_width
                        depth = depth_value - depth_value_initial
                        depth_value = depth_value_initial
                            
                    if (torso_width * 1.4) < torso_height:
                        depth_value = torso_height
                        depth = depth_value - depth_value_initial
                        depth_value = depth_value_initial
                            
#                    Pose = bpy.data.objects["Pose"]
 #                   pose_x = Pose.location.x
  #                  pose_z = Pose.location.z 
   #                     
    #                    
     #               Pose.location = (pose_x, ((-2 * depth) + 1), pose_z)
      #              Pose.keyframe_insert(data_path="location", frame = xl)
                    
                    
                    
                        
                    if hip_rot_z == 0:
                        hip_rot_z = hip_rot_z + 0.0001
                            
#                    if torso_slope > 0.0000:
 #                       hip_rot = (((((np.arcsin(hip_rot_z))))*10) - 1)
  #                      hip_rot_final = hip_rot - hip_rot_initial
   #                     hip_2.rotation_euler = (0, 0, hip_rot_final)
    #                    hip_2.keyframe_insert(data_path="rotation_euler", frame = xl)
     #                   hip_rot_initial = hip_rot
      #              if torso_slope < 0.0000:
       #                 hip_rot = (((((np.arcsin(hip_rot_z))))*10) - 1)
        #                hip_rot_final = hip_rot - hip_rot_initial
         #               hip_2.rotation_euler = (0, 0, -hip_rot_final)
          #              hip_2.keyframe_insert(data_path="rotation_euler", frame = xl)
           #             hip_rot_initial = hip_rot
            #        if torso_slope == 0:
             #           hip_2.rotation_euler = (0, 0, 0)
              #          hip_2.keyframe_insert(data_path="rotation_euler", frame = xl)
                        
                    


#            if results.left_hand_landmarks:
 #               bns = [b for b in results.left_hand_landmarks.landmark]
  #              scale = 2
   #             bones = sorted(hand_left.children, key=lambda b: b.name)
    #            for k in range(21):
     #               bones[k].location.y = (bns[k].z)*scale
      #              bones[k].location.x = (0.5-bns[k].x)*scale
       #             bones[k].location.z = (0.5-bns[k].y)*scale
        #            bones[k].keyframe_insert(data_path="location", frame=xl)

#            if results.right_hand_landmarks:
 #               bns = [b for b in results.right_hand_landmarks.landmark]
  #              scale = 2
   #             bones = sorted(hand_right.children, key=lambda b: b.name)
    #            for k in range(21):
     #               bones[k].location.y = (bns[k].z)*scale
      #              bones[k].location.x = (0.5-bns[k].x)*scale
       #             bones[k].location.z = (0.5-bns[k].y)*scale
        #            bones[k].keyframe_insert(data_path="location", frame=xl)

            if results.face_landmarks:
                bns = [b for b in results.face_landmarks.landmark]
                scale = 2
                bones = sorted(face.children, key=lambda b: b.name)

                top = scene.objects.get("013Face")
                bottom = scene.objects.get("014Face")
                right = scene.objects.get("078Face")
                left = scene.objects.get("308Face")
                
                top.location.y = (bns[13].z)*scale
                top.location.x = (0.5-bns[13].x)*scale
                top.location.z = (0.5-bns[13].y)*scale
                top.keyframe_insert(data_path="location", frame=xl)
                
                bottom.location.y = (bns[14].z)*scale
                bottom.location.x = (0.5-bns[14].x)*scale
                bottom.location.z = (0.5-bns[14].y)*scale
                bottom.keyframe_insert(data_path="location", frame=xl)
                
                right.location.y = (bns[78].z)*scale
                right.location.x = (0.5-bns[78].x)*scale
                right.location.z = (0.5-bns[78].y)*scale
                right.keyframe_insert(data_path="location", frame=xl)
                
                left.location.y = (bns[308].z)*scale
                left.location.x = (0.5-bns[308].x)*scale
                left.location.z = (0.5-bns[308].y)*scale
                left.keyframe_insert(data_path="location", frame=xl)
                    
                context = bpy.context
                scene = context.scene
                mytool = scene.settings
                
                
                import math
                
                initial_mouth_ratio = 0
                
                
                
 
                if l_xl < xl:
                    
                    top = scene.objects.get("013Face")
                    bottom = scene.objects.get("014Face")
                    right = scene.objects.get("078Face")
                    left = scene.objects.get("308Face")
                    o = scene.objects.get("419Face")
                    l = scene.objects.get("196Face")
                    
                    vert_dis = math.sqrt((top.location.x - bottom.location.x)**2) + ((top.location.z - bottom.location.z)**2)
                    horz_dis = math.sqrt((right.location.x - left.location.x)**2) + ((right.location.z - left.location.z)**2)
                    
                    
                    mouth_ratio = vert_dis / horz_dis
                    new_mouth_ratio = mouth_ratio - initial_mouth_ratio
                    
                    ref_size = math.sqrt((o.location.x - l.location.x)**2) + ((o.location.z - l.location.z)**2)

                    current_armature = (mytool.eyedropper)
                    new_armature = bpy.data.objects[current_armature]
                    
                    m_top_loc = new_armature.pose.bones["lip.B"]
                    m_bottom_loc = new_armature.pose.bones["lip.T"]
                    chin_loc = new_armature.pose.bones["chin"]

                    
                    
                    m_bottom = new_armature.pose.bones["lip.B"].location.z
                    m_top = new_armature.pose.bones["lip.T"].location.z
                    chin = new_armature.pose.bones["chin"].location.z

                    
                    
                    m_top_loc.location.y = m_top - (new_mouth_ratio / 10)
                    m_bottom_loc.location.y = m_bottom + (new_mouth_ratio / 10)
                    chin_loc.location.y = chin - (new_mouth_ratio / 15)

                    
                    
                    m_top_loc.keyframe_insert(data_path="location", frame=xl)
                    m_bottom_loc.keyframe_insert(data_path="location", frame=xl)
                    chin_loc.keyframe_insert(data_path="location", frame=xl)


                    
                    initial_mouth_ratio = mouth_ratio


                
                    
                            


            mp_drawing.draw_landmarks(
            image, results.face_landmarks, mp_holistic.FACEMESH_CONTOURS)

#            mp_drawing.draw_landmarks(
 #           image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

#            mp_drawing.draw_landmarks(
 #           image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

            mp_drawing.draw_landmarks(
            image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)

            image = cv2.flip(image, 1)
            cv2.imshow('MediaPipe Holistic', image)
            if cv2.waitKey(1) & 0xFF == 27:
                break

            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            bpy.context.scene.frame_set(n)

    cap.release()
    cv2.destroyAllWindows()
    
    
    
    
def run_face(file_path):
    
    try:
        import cv2
        import mediapipe as mp
    except Exception as e:
        # bpy.ops.message.messagebox('INVOKE_DEFAULT', message = 'Installing additional libraries, this may take a moment...')
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        #install()
        import cv2
        import mediapipe as mp
        
    delete_stretch()

    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    body = body_setup()
    face = full_setup()
    #hand_left, hand_right, face = full_setup()

    mp_drawing = mp.solutions.drawing_utils
    mp_holistic = mp.solutions.holistic

    if file_path == "None": cap = cv2.VideoCapture(0)
    else: cap = cv2.VideoCapture(file_path)

    with mp_holistic.Holistic(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as holistic:

        for n in range(9000):
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            # image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = holistic.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            xl = bpy.data.scenes[0].frame_current
            l_xl = xl - 1
                
                
            context = bpy.context
            scene = context.scene  
            mytool = scene.settings
    
    
    
            if results.face_landmarks:
                bns = [b for b in results.face_landmarks.landmark]
                scale = 2
                bones = sorted(face.children, key=lambda b: b.name)
                
                top = scene.objects.get("013Face")
                bottom = scene.objects.get("014Face")
                right = scene.objects.get("078Face")
                left = scene.objects.get("308Face")
                
                top.location.y = (bns[13].z)*scale
                top.location.x = (0.5-bns[13].x)*scale
                top.location.z = (0.5-bns[13].y)*scale
                top.keyframe_insert(data_path="location", frame=xl)
                
                bottom.location.y = (bns[14].z)*scale
                bottom.location.x = (0.5-bns[14].x)*scale
                bottom.location.z = (0.5-bns[14].y)*scale
                bottom.keyframe_insert(data_path="location", frame=xl)
                
                right.location.y = (bns[78].z)*scale
                right.location.x = (0.5-bns[78].x)*scale
                right.location.z = (0.5-bns[78].y)*scale
                right.keyframe_insert(data_path="location", frame=xl)
                
                left.location.y = (bns[308].z)*scale
                left.location.x = (0.5-bns[308].x)*scale
                left.location.z = (0.5-bns[308].y)*scale
                left.keyframe_insert(data_path="location", frame=xl)
                
                    
                context = bpy.context
                scene = context.scene
                mytool = scene.settings
                
                
                import math
                
                initial_mouth_ratio = 0
                
                
                
 
                if l_xl < xl:
                    
                    top = scene.objects.get("013Face")
                    bottom = scene.objects.get("014Face")
                    right = scene.objects.get("078Face")
                    left = scene.objects.get("308Face")
                    o = scene.objects.get("419Face")
                    l = scene.objects.get("196Face")
                    
                    vert_dis = math.sqrt((top.location.x - bottom.location.x)**2) + ((top.location.z - bottom.location.z)**2)
                    horz_dis = math.sqrt((right.location.x - left.location.x)**2) + ((right.location.z - left.location.z)**2)
                    
                    
                    mouth_ratio = vert_dis / horz_dis
                    new_mouth_ratio = mouth_ratio - initial_mouth_ratio
                    
                    ref_size = math.sqrt((o.location.x - l.location.x)**2) + ((o.location.z - l.location.z)**2)

                    current_armature = (mytool.eyedropper)
                    new_armature = bpy.data.objects[current_armature]
                    
                    m_top_loc = new_armature.pose.bones["lip.B"]
                    m_bottom_loc = new_armature.pose.bones["lip.T"]
                    chin_loc = new_armature.pose.bones["chin"]

                    
                    
                    m_bottom = new_armature.pose.bones["lip.B"].location.z
                    m_top = new_armature.pose.bones["lip.T"].location.z
                    chin = new_armature.pose.bones["chin"].location.z

                    
                    
                    m_top_loc.location.y = m_top - (new_mouth_ratio / 10)
                    m_bottom_loc.location.y = m_bottom + (new_mouth_ratio / 10)
                    chin_loc.location.y = chin - (new_mouth_ratio / 15)

                    
                    
                    m_top_loc.keyframe_insert(data_path="location", frame=xl)
                    m_bottom_loc.keyframe_insert(data_path="location", frame=xl)
                    chin_loc.keyframe_insert(data_path="location", frame=xl)


                    
                    initial_mouth_ratio = mouth_ratio


                
                    
                            


            mp_drawing.draw_landmarks(
            image, results.face_landmarks, mp_holistic.FACEMESH_CONTOURS)

#            mp_drawing.draw_landmarks(
 #           image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

#            mp_drawing.draw_landmarks(
 #           image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

            mp_drawing.draw_landmarks(
            image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)

            image = cv2.flip(image, 1)
            cv2.imshow('MediaPipe Holistic', image)
            if cv2.waitKey(1) & 0xFF == 27:
                break

            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            bpy.context.scene.frame_set(n)

    cap.release()
    cv2.destroyAllWindows()
    
    
        
        
def body_setup():
    """ Setup tracking markers for body tracking """
    scene_objects = [n for n in bpy.context.scene.objects.keys()]
    setup = "Pose" in scene_objects

    if not setup:
        bpy.ops.object.add(radius=1.0, type='EMPTY')
        pose = bpy.context.active_object
        pose.name = "Pose"

        bpy.ops.object.add(radius=1.0, type='EMPTY')
        body = bpy.context.active_object
        body.name = "Body"
        body.parent = pose

        for k in range(33):
            bpy.ops.object.add(radius=1.0, type='EMPTY')
            box = bpy.context.active_object
            box.name = body_names[k]
            box.scale = (0.01, 0.01, 0.01)
            box.parent = body
        
        context = bpy.context
        scene = context.scene

        mytool = scene.settings

        selected_armature = scene.objects.get(mytool.eyedropper)
        
        r = scene.objects.get("20 right index")
        l = scene.objects.get("19 left index")
        
        r.rotation_euler = (0, -210, 0)
        l.rotation_euler = (0, -210, 0)
        
        bpy.ops.object.add(radius=1.0, type='EMPTY')
        box = bpy.context.active_object
        box.name = "Left Hand"
        box.scale = (0.01, 0.01, 0.01)
        clc = box.constraints.new('COPY_ROTATION')
        clc.target = selected_armature
        clc.subtarget = "DEF-forearm.L.001"
                
        bpy.ops.object.add(radius=1.0, type='EMPTY')
        box = bpy.context.active_object
        box.name = "Right Hand"
        box.scale = (0.01, 0.01, 0.01)
        clc = box.constraints.new('COPY_ROTATION')
        clc.target = selected_armature
        clc.subtarget = "DEF-forearm.R.001"
        
    body = bpy.context.scene.objects["Body"]
    return body



        

def draw_file_opener(self, context):
    layout = self.layout
    scn = context.scene
    col = layout.column()
    row = col.row(align=True)
    row.prop(scn.settings, 'file_path', text='directory:')
    row.operator("something.identifier_selector", icon="FILE_FOLDER", text="")
    
    
class Settings(PropertyGroup):
    smoothing: bpy.props.FloatProperty(name = "Animation Smoothing",
                            description = "Smoothing between 0 and 1",
                            min = 0.0,
                            max = 1.0,
                            default = 0.1)

    file_path = bpy.props.StringProperty()
    
    file_name : bpy.props.StringProperty(name = "File Path:")
    

    # Capture only body pose if True, otherwise capture hands, face and body
    body_tracking = bpy.props.BoolProperty(default=True)
    
    eyedropper : bpy.props.StringProperty(name = "Armature")
    
    smooth_val : bpy.props.FloatProperty(name = "Smooth Value", min = 0, max = 10)
    
    target : bpy.props.StringProperty(name = "Target")
    
    source : bpy.props.StringProperty(name = "Source")
    
    

class RunOperator(bpy.types.Operator):
    """Capture Motion"""
    bl_idname = "object.run_body_operator"
    bl_label = "Run Body Operator"

    def execute(self, context):
        if context.scene.settings.body_tracking: run_full("None")
        else: 
            run_full("None")
        return {'FINISHED'}
    
class RunOperator_Face(bpy.types.Operator):
    """Capture Face Motion"""
    bl_idname = "object.run_body_operator_face"
    bl_label = "Run Face Operator"

    def execute(self, context):
        if context.scene.settings.body_tracking: run_face("None")
        else: 
            run_face("None")
        return {'FINISHED'}
    
    
class RunFileSelector(bpy.types.Operator, ImportHelper):
    """Import Video"""
    bl_idname = "something.identifier_selector"
    bl_label = "some folder"
    filename_ext = ""

    def execute(self, context):
        file_name = self.properties.filepath
        run_full(file_name)
        return{'FINISHED'} 
    
class RunFileSelector_Face(bpy.types.Operator, ImportHelper):
    """Import Video (Face)"""
    bl_idname = "something.identifier_selector_face"
    bl_label = "some folder"
    filename_ext = ""

    def execute(self, context):
        file_name = self.properties.filepath
        run_face(file_name)
        return{'FINISHED'} 
    
    
    
class AddArmature(bpy.types.Operator):
    """Add Rig"""
    bl_idname = "object.add_rig"
    bl_label = "Add Rig"
    
    
    def execute(self, context):
        import rigify
        bpy.ops.object.armature_human_metarig_add()
        bpy.ops.object.mode_set(mode='OBJECT')
        for obj in bpy.context.selected_objects:
            rig_name = obj.name
        context = bpy.context
        scene = bpy.context.scene
        mrig = bpy.data.objects[rig_name]
        rigify.generate.generate_rig(context, mrig)
        return {'FINISHED'}
    
    
    
         
    
class MessageBox(bpy.types.Operator):
    bl_idname = "message.messagebox"
    bl_label = ""

    message = bpy.props.StringProperty(
        name = "message",
        description = "message",
        default = 'Installing additional libraries, this may take a moment...'
    )

    def execute(self, context):
        self.report({'INFO'}, self.message)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 400)

    def draw(self, context):
        self.layout.label(text=self.message)


class BlenderMocapPanel(bpy.types.Panel):
    bl_label = "Blender Mocap 2"
    bl_category = "Blender Mocap 2"
    bl_idname = "Blender Mocap 2"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Blender Mocap 2"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        settings = context.scene.settings
        scene = context.scene
        mytool = scene.settings
        
        row = layout.row()
        row.label(text="Select an Armature")
        
        layout.prop_search(mytool, "eyedropper", context.scene, "objects")
        
        row = layout.row()
        row.label(text="Run Motion Capture")

        row = layout.row()
        row.operator(RunOperator.bl_idname, text="Capture Motion", icon="CAMERA_DATA")
        
        row = layout.row()
        row.operator(RunOperator_Face.bl_idname, text="Capture Face Motion", icon="CAMERA_DATA")
        
        row = layout.row()
        row.operator(RunFileSelector.bl_idname, text="Import Video", icon="SEQUENCE")
        
        row = layout.row()
        row.operator(RunFileSelector_Face.bl_idname, text="Import Video (Face)", icon="SEQUENCE")
        
        row = layout.row()
        row.operator(AddArmature.bl_idname, text="Add Rig", icon="OUTLINER_OB_ARMATURE")
        
        row = layout.row()
        row.operator(TransferAnimation.bl_idname, text="Transfer Animation", icon="FILE_TICK")

        row = layout.row()
        row.label(text="(Press (esc) to stop)")

        row = layout.row()
        row.label(text="Select the rig and drivers")

        row = layout.row()
        row.operator(SelectSystem.bl_idname, text="Select System", icon="RESTRICT_SELECT_OFF")
        
        layout.prop(mytool, "smooth_val")
        
        row = layout.row()
        row.operator(Smooth_animation.bl_idname, text = "Smooth Animation", icon="IPO_BEZIER")
        
        row = layout.row()
        row.label(text="Save Animation to Armature")
        
        row = layout.row()
        row.operator(Save_Animation.bl_idname, text = "Save Animation", icon="DECORATE_DRIVER")
        
        row = layout.row()
        row.label(text="Retarget Animation from Rokoko")
        
        layout.prop_search(mytool, "source", context.scene, "objects")
        
        layout.prop_search(mytool, "target", context.scene, "objects")
        
        row = layout.row()
        row.operator(Link.bl_idname, text = "Link Armatures", icon="DECORATE_LINKED")
        
        row = layout.row()
        row.operator(Retarget.bl_idname, text = "Retarget Animation", icon="INDIRECT_ONLY_OFF")
        
        row = layout.row()
        row.operator(DeleteConstraints.bl_idname, text = "Delete Constraints", icon="CANCEL")
        
        row = layout.row()
        row.operator(DeleteEmpties.bl_idname, text = "Delete Empties", icon="CANCEL")

        row = layout.row()
        label = "Body" if settings.body_tracking else "Body, Hands and Face"
        row.prop(settings, 'body_tracking', text=label, toggle=True)
        
        context = bpy.context     
        scene = context.scene
        mytool = scene.settings
        
        
def delete_constraints(target):
    
    context = bpy.context     
    scene = context.scene
    mytool = scene.settings

    target = scene.objects.get(mytool.target)
    
    constraint_bones = [
    "head",
    "neck", "tweak_spine.004",
    "tweak_spine.003",
    "tweak_spine.002",
    "tweak_spine.001",
    "torso",
    "shoulder.L",
    "shoulder.R",
    "upper_arm_tweak.L",
    "upper_arm_tweak.R",
    "forearm_tweak.L",
    "forearm_tweak.R",
    "hand_ik.L",
    "hand_ik.R",
    "shin_tweak.L",
    "shin_tweak.R",
    "foot_ik.L",
    "foot_ik.R",
    "root",
    "thigh_ik.R",
    "thigh_ik.L",
    "upper_arm_ik.R",
    "upper_arm_ik.L",
    "chest",
    "spine_fk.002"
    ]
    
    for k in range(4):
        for n in range(26):
            if target.pose.bones[constraint_bones[n]].constraints:
                target.pose.bones[constraint_bones[n]].constraints.remove(target.pose.bones[constraint_bones[n]].constraints[0])
                
    hips = target.pose.bones.get("hips")            
    hips.location = (0, 0, 0)
    hips.keyframe_insert(data_path="location", frame=bpy.data.scenes[0].frame_start)            
    
                
def delete_empties():

    if bpy.data.collections["Empties.001"]:
        
        empties = bpy.data.collections["Empties.001"]
        
        for obj in empties.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        
        
                
def align_rig(target):
    
    context = bpy.context     
    scene = context.scene
    mytool = scene.settings

    target = scene.objects.get(mytool.target)
    
    target.scale = (0.875, 0.875, 0.875)
    
    l_hand = target.pose.bones.get("hand_ik.L")
    l_hand.location = (0.089375, 0, 0.302197)
    l_hand.rotation_quaternion = (0.941769, -0.074239, 0.033559, 0.326242)
    
    r_hand = target.pose.bones.get("hand_ik.R")
    r_hand.location = (-0.089375, 0, 0.302197)
    r_hand.rotation_quaternion = (0.941769, -0.074239, 0.033559, -0.326242)
    
    torso = target.pose.bones.get("torso")
    torso.location = (0, 0.05, 0)
    
        
def link_rok(source, target):
    
    context = bpy.context     
    scene = context.scene
    mytool = scene.settings

    source = scene.objects.get(mytool.source)
    target = scene.objects.get(mytool.target)
    
    delete_constraints(target)
    
    empties_col = bpy.data.collections.new("Empties.001")
    bpy.context.scene.collection.children.link(empties_col)
        
    empties = bpy.data.collections["Empties.001"]
    
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(0.025, 0.025, 0.025))
    l_empty = bpy.context.active_object
    l_empty.scale = (0.025, 0.025, 0.025)
    l_empty.name = "Left Foot Empty"
    empties.objects.link(l_empty)
    l_con = scene.objects.get("Left Foot Empty")
    clc = l_con.constraints.new('CHILD_OF')
    clc.target = source
    clc.subtarget = "LeftFoot"
    
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(0.025, 0.025, 0.025))
    r_empty = bpy.context.active_object
    r_empty.scale = (0.025, 0.025, 0.025)
    r_empty.name = "Right Foot Empty"
    empties.objects.link(r_empty)
    r_con = scene.objects.get("Right Foot Empty")
    clc = r_con.constraints.new('CHILD_OF')
    clc.target = source
    clc.subtarget = "RightFoot"
    
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(0.025, 0.025, 0.025))
    lh_empty = bpy.context.active_object
    lh_empty.scale = (0.025, 0.025, 0.025)
    lh_empty.name = "Left Hand Empty"
    empties.objects.link(lh_empty)
    lh_con = scene.objects.get("Left Hand Empty")
    clc = lh_con.constraints.new('CHILD_OF')
    clc.target = source
    clc.subtarget = "LeftHand"
    lh_con.rotation_euler = (0, 1.57, -1.57)
    
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(0.025, 0.025, 0.025))
    rh_empty = bpy.context.active_object
    rh_empty.scale = (0.025, 0.025, 0.025)
    rh_empty.name = "Right Hand Empty"
    empties.objects.link(rh_empty)
    rh_con = scene.objects.get("Right Hand Empty")
    clc = rh_con.constraints.new('CHILD_OF')
    clc.target = source
    clc.subtarget = "RightHand"
    rh_con.rotation_euler = (0, -1.57, 1.57)
    
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(0.025, 0.025, 0.025))
    head_empty = bpy.context.active_object
    head_empty.scale = (0.025, 0.025, 0.025)
    head_empty.name = "Head Empty"
    empties.objects.link(head_empty)
    head_con = scene.objects.get("Head Empty")
    clc = head_con.constraints.new('CHILD_OF')
    clc.target = source
    clc.subtarget = "Head"
    head_con.rotation_euler = (1.57, 0, 0)
    
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(0.025, 0.025, 0.025))
    r_shin_empty = bpy.context.active_object
    r_shin_empty.scale = (0.025, 0.025, 0.025)
    r_shin_empty.name = "R Shin Empty"
    empties.objects.link(r_shin_empty)
    r_shin_con = scene.objects.get("R Shin Empty")
    clc = r_shin_con.constraints.new('CHILD_OF')
    clc.target = source
    clc.subtarget = "RightThigh"
    r_shin_con.rotation_euler = (-1.57, 0, 0)
    
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(0.025, 0.025, 0.025))
    l_shin_empty = bpy.context.active_object
    l_shin_empty.scale = (0.025, 0.025, 0.025)
    l_shin_empty.name = "L Shin Empty"
    empties.objects.link(l_shin_empty)
    l_shin_con = scene.objects.get("L Shin Empty")
    clc = l_shin_con.constraints.new('CHILD_OF')
    clc.target = source
    clc.subtarget = "LeftThigh"
    l_shin_con.rotation_euler = (-1.57, 0, 0)
    
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(0.025, 0.025, 0.025))
    shoulder_empty = bpy.context.active_object
    shoulder_empty.scale = (0.025, 0.025, 0.025)
    shoulder_empty.name = "Shoulder Empty"
    empties.objects.link(shoulder_empty)
    shoulder_con = scene.objects.get("Shoulder Empty")
    clc = shoulder_con.constraints.new('CHILD_OF')
    clc.target = source
    clc.subtarget = "Spine4"
    shoulder_con.rotation_euler = (0, 0, 0)
    
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(0.025, 0.025, 0.025))
    rf_arm_empty = bpy.context.active_object
    rf_arm_empty.scale = (0.025, 0.025, 0.025)
    rf_arm_empty.name = "rf_arm Empty"
    empties.objects.link(rf_arm_empty)
    rf_arm_con = scene.objects.get("rf_arm Empty")
    clc = rf_arm_con.constraints.new('CHILD_OF')
    clc.target = source
    clc.subtarget = "RightArm"
    rf_arm_con.rotation_euler = (0, -1.57, 0)
    
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(0.025, 0.025, 0.025))
    lf_arm_empty = bpy.context.active_object
    lf_arm_empty.scale = (0.025, 0.025, 0.025)
    lf_arm_empty.name = "lf_arm Empty"
    empties.objects.link(lf_arm_empty)
    lf_arm_con = scene.objects.get("lf_arm Empty")
    clc = lf_arm_con.constraints.new('CHILD_OF')
    clc.target = source
    clc.subtarget = "LeftArm"
    lf_arm_con.rotation_euler = (0, 1.57, 0)

    
    
    rig_bones = [
    "head",
    "neck", "tweak_spine.004",
    "tweak_spine.003",
    "tweak_spine.002",
    "tweak_spine.001",
    "torso",
    "shoulder.L",
    "shoulder.R",
    "upper_arm_tweak.L",
    "upper_arm_tweak.R",
    "forearm_tweak.L",
    "forearm_tweak.R",
    "hand_ik.L",
    "hand_ik.R",
    "shin_tweak.L",
    "shin_tweak.R",
    "foot_ik.L",
    "foot_ik.R",
    ]
    
    rok_bones = [
    "Head",
    "Neck", "Neck",
    "Spine4",
    "Spine3",
    "Spine1",
    "Hips",
    "LeftShoulder",
    "RightShoulder",
    "LeftArm",
    "RightArm",
    "LeftForeArm",
    "RightForeArm",
    "LeftHand",
    "RightHand",
    "LeftShin",
    "RightShin",
    "LeftFoot",
    "RightFoot"
    ]
    
    for k in range(19):
        rig_bone = rig_bones[k]
        new_bone = target.pose.bones.get(rig_bone)
        
        rok_bone = source.pose.bones.get(rok_bones[k])
        
        clc = new_bone.constraints.new("COPY_LOCATION")
        clc.target = source
        clc.subtarget = rok_bones[k]
    
    torso = target.pose.bones.get("torso")
    crc = torso.constraints.new("COPY_ROTATION")
    crc.target = source
    crc.subtarget = "Hips"
    target.pose.bones["torso"].constraints["Copy Rotation"].use_x = False
    
    r_shoulder = target.pose.bones.get("shoulder.R")
    crc = r_shoulder.constraints.new("COPY_ROTATION")
    crc.target = source
    crc.subtarget = "RightShoulder"
    target.pose.bones["shoulder.R"].constraints["Copy Rotation"].use_y = False
    
    l_shoulder = target.pose.bones.get("shoulder.L")
    crc = l_shoulder.constraints.new("COPY_ROTATION")
    crc.target = source
    crc.subtarget = "LeftShoulder"
    target.pose.bones["shoulder.L"].constraints["Copy Rotation"].use_y = False
    
    l_foot = target.pose.bones.get("foot_ik.L")
    crc = l_foot.constraints.new("COPY_ROTATION")
    crc.target = l_con
    
    r_foot = target.pose.bones.get("foot_ik.R")
    crc = r_foot.constraints.new("COPY_ROTATION")
    crc.target = r_con
    
    l_hand = target.pose.bones.get("hand_ik.L")
    crc = l_hand.constraints.new("COPY_ROTATION")
    crc.target = lh_con
    
    r_hand = target.pose.bones.get("hand_ik.R")
    crc = r_hand.constraints.new("COPY_ROTATION")
    crc.target = rh_con
    
    head = target.pose.bones.get("head")
    crc = head.constraints.new("COPY_ROTATION")
    crc.target = head_con
    
    r_shin = target.pose.bones.get("thigh_ik.R")
    crc = r_shin.constraints.new("COPY_ROTATION")
    crc.target = r_shin_con
    
    l_shin = target.pose.bones.get("thigh_ik.L")
    crc = l_shin.constraints.new("COPY_ROTATION")
    crc.target = l_shin_con
    
    shoulders = target.pose.bones.get("chest")
    crc = shoulders.constraints.new("COPY_ROTATION")
    crc.target = shoulder_con
    
    r_forearm = target.pose.bones.get("upper_arm_ik.R")
    crc = r_forearm.constraints.new("COPY_ROTATION")
    crc.target = rf_arm_con
    
    l_forearm = target.pose.bones.get("upper_arm_ik.L")
    crc = l_forearm.constraints.new("COPY_ROTATION")
    crc.target = lf_arm_con
    
    spine_four = target.pose.bones.get("tweak_spine.004")
    head = target.pose.bones.get("head")
    
    r_shoulder.constraints.remove(r_shoulder.constraints[0])
    l_shoulder.constraints.remove(l_shoulder.constraints[0])
    spine_four.constraints.remove(spine_four.constraints[0])
    head.constraints.remove(head.constraints[0])
    
    target.pose.bones["neck"].constraints["Copy Location"].influence = 0.5
    
    hips = target.pose.bones.get("hips")
    hips.location = (0, 0.07, 0)
    hips.keyframe_insert(data_path="location", frame=bpy.data.scenes[0].frame_start)
    
    
def retarget_rok(source, target):
    
    context = bpy.context     
    scene = context.scene
    mytool = scene.settings

    source = scene.objects.get(mytool.source)
    target = scene.objects.get(mytool.target)
    
    delete_constraints(target)
    
    empties_col = bpy.data.collections.new("Empties.001")
    bpy.context.scene.collection.children.link(empties_col)
        
    empties = bpy.data.collections["Empties.001"]
    
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(0.025, 0.025, 0.025))
    l_empty = bpy.context.active_object
    l_empty.scale = (0.025, 0.025, 0.025)
    l_empty.name = "Left Foot Empty"
    empties.objects.link(l_empty)
    l_con = scene.objects.get("Left Foot Empty")
    clc = l_con.constraints.new('CHILD_OF')
    clc.target = source
    clc.subtarget = "LeftFoot"
    
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(0.025, 0.025, 0.025))
    r_empty = bpy.context.active_object
    r_empty.scale = (0.025, 0.025, 0.025)
    r_empty.name = "Right Foot Empty"
    empties.objects.link(r_empty)
    r_con = scene.objects.get("Right Foot Empty")
    clc = r_con.constraints.new('CHILD_OF')
    clc.target = source
    clc.subtarget = "RightFoot"
    
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(0.025, 0.025, 0.025))
    lh_empty = bpy.context.active_object
    lh_empty.scale = (0.025, 0.025, 0.025)
    lh_empty.name = "Left Hand Empty"
    empties.objects.link(lh_empty)
    lh_con = scene.objects.get("Left Hand Empty")
    clc = lh_con.constraints.new('CHILD_OF')
    clc.target = source
    clc.subtarget = "LeftHand"
    lh_con.rotation_euler = (0, 1.57, -1.57)
    
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(0.025, 0.025, 0.025))
    rh_empty = bpy.context.active_object
    rh_empty.scale = (0.025, 0.025, 0.025)
    rh_empty.name = "Right Hand Empty"
    empties.objects.link(rh_empty)
    rh_con = scene.objects.get("Right Hand Empty")
    clc = rh_con.constraints.new('CHILD_OF')
    clc.target = source
    clc.subtarget = "RightHand"
    rh_con.rotation_euler = (0, -1.57, 1.57)
    
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(0.025, 0.025, 0.025))
    head_empty = bpy.context.active_object
    head_empty.scale = (0.025, 0.025, 0.025)
    head_empty.name = "Head Empty"
    empties.objects.link(head_empty)
    head_con = scene.objects.get("Head Empty")
    clc = head_con.constraints.new('CHILD_OF')
    clc.target = source
    clc.subtarget = "Head"
    head_con.rotation_euler = (1.57, 0, 0)
    
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(0.025, 0.025, 0.025))
    r_shin_empty = bpy.context.active_object
    r_shin_empty.scale = (0.025, 0.025, 0.025)
    r_shin_empty.name = "R Shin Empty"
    empties.objects.link(r_shin_empty)
    r_shin_con = scene.objects.get("R Shin Empty")
    clc = r_shin_con.constraints.new('CHILD_OF')
    clc.target = source
    clc.subtarget = "RightThigh"
    r_shin_con.rotation_euler = (-1.57, 0, 0)
    
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(0.025, 0.025, 0.025))
    l_shin_empty = bpy.context.active_object
    l_shin_empty.scale = (0.025, 0.025, 0.025)
    l_shin_empty.name = "L Shin Empty"
    empties.objects.link(l_shin_empty)
    l_shin_con = scene.objects.get("L Shin Empty")
    clc = l_shin_con.constraints.new('CHILD_OF')
    clc.target = source
    clc.subtarget = "LeftThigh"
    l_shin_con.rotation_euler = (-1.57, 0, 0)
    
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(0.025, 0.025, 0.025))
    shoulder_empty = bpy.context.active_object
    shoulder_empty.scale = (0.025, 0.025, 0.025)
    shoulder_empty.name = "Shoulder Empty"
    empties.objects.link(shoulder_empty)
    shoulder_con = scene.objects.get("Shoulder Empty")
    clc = shoulder_con.constraints.new('CHILD_OF')
    clc.target = source
    clc.subtarget = "Spine4"
    shoulder_con.rotation_euler = (0, 0, 0)
    
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(0.025, 0.025, 0.025))
    rf_arm_empty = bpy.context.active_object
    rf_arm_empty.scale = (0.025, 0.025, 0.025)
    rf_arm_empty.name = "rf_arm Empty"
    empties.objects.link(rf_arm_empty)
    rf_arm_con = scene.objects.get("rf_arm Empty")
    clc = rf_arm_con.constraints.new('CHILD_OF')
    clc.target = source
    clc.subtarget = "RightArm"
    rf_arm_con.rotation_euler = (0, -1.57, 0)
    
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(0.025, 0.025, 0.025))
    lf_arm_empty = bpy.context.active_object
    lf_arm_empty.scale = (0.025, 0.025, 0.025)
    lf_arm_empty.name = "lf_arm Empty"
    empties.objects.link(lf_arm_empty)
    lf_arm_con = scene.objects.get("lf_arm Empty")
    clc = lf_arm_con.constraints.new('CHILD_OF')
    clc.target = source
    clc.subtarget = "LeftArm"
    lf_arm_con.rotation_euler = (0, 1.57, 0)

    
    
    rig_bones = [
    "head",
    "neck", "tweak_spine.004",
    "tweak_spine.003",
    "tweak_spine.002",
    "tweak_spine.001",
    "torso",
    "shoulder.L",
    "shoulder.R",
    "upper_arm_tweak.L",
    "upper_arm_tweak.R",
    "forearm_tweak.L",
    "forearm_tweak.R",
    "hand_ik.L",
    "hand_ik.R",
    "shin_tweak.L",
    "shin_tweak.R",
    "foot_ik.L",
    "foot_ik.R",
    ]
    
    rok_bones = [
    "Head",
    "Neck", "Neck",
    "Spine4",
    "Spine3",
    "Spine1",
    "Hips",
    "LeftShoulder",
    "RightShoulder",
    "LeftArm",
    "RightArm",
    "LeftForeArm",
    "RightForeArm",
    "LeftHand",
    "RightHand",
    "LeftShin",
    "RightShin",
    "LeftFoot",
    "RightFoot"
    ]
    
    for k in range(19):
        rig_bone = rig_bones[k]
        new_bone = target.pose.bones.get(rig_bone)
        
        rok_bone = source.pose.bones.get(rok_bones[k])
        
        clc = new_bone.constraints.new("COPY_LOCATION")
        clc.target = source
        clc.subtarget = rok_bones[k]
    
    torso = target.pose.bones.get("torso")
    crc = torso.constraints.new("COPY_ROTATION")
    crc.target = source
    crc.subtarget = "Hips"
    target.pose.bones["torso"].constraints["Copy Rotation"].use_x = False
    
    r_shoulder = target.pose.bones.get("shoulder.R")
    crc = r_shoulder.constraints.new("COPY_ROTATION")
    crc.target = source
    crc.subtarget = "RightShoulder"
    target.pose.bones["shoulder.R"].constraints["Copy Rotation"].use_y = False
    
    l_shoulder = target.pose.bones.get("shoulder.L")
    crc = l_shoulder.constraints.new("COPY_ROTATION")
    crc.target = source
    crc.subtarget = "LeftShoulder"
    target.pose.bones["shoulder.L"].constraints["Copy Rotation"].use_y = False
    
    l_foot = target.pose.bones.get("foot_ik.L")
    crc = l_foot.constraints.new("COPY_ROTATION")
    crc.target = l_con
    
    r_foot = target.pose.bones.get("foot_ik.R")
    crc = r_foot.constraints.new("COPY_ROTATION")
    crc.target = r_con
    
    l_hand = target.pose.bones.get("hand_ik.L")
    crc = l_hand.constraints.new("COPY_ROTATION")
    crc.target = lh_con
    
    r_hand = target.pose.bones.get("hand_ik.R")
    crc = r_hand.constraints.new("COPY_ROTATION")
    crc.target = rh_con
    
    head = target.pose.bones.get("head")
    crc = head.constraints.new("COPY_ROTATION")
    crc.target = head_con
    
    r_shin = target.pose.bones.get("thigh_ik.R")
    crc = r_shin.constraints.new("COPY_ROTATION")
    crc.target = r_shin_con
    
    l_shin = target.pose.bones.get("thigh_ik.L")
    crc = l_shin.constraints.new("COPY_ROTATION")
    crc.target = l_shin_con
    
    shoulders = target.pose.bones.get("chest")
    crc = shoulders.constraints.new("COPY_ROTATION")
    crc.target = shoulder_con
    
    r_forearm = target.pose.bones.get("upper_arm_ik.R")
    crc = r_forearm.constraints.new("COPY_ROTATION")
    crc.target = rf_arm_con
    
    l_forearm = target.pose.bones.get("upper_arm_ik.L")
    crc = l_forearm.constraints.new("COPY_ROTATION")
    crc.target = lf_arm_con
    
    spine_four = target.pose.bones.get("tweak_spine.004")
    head = target.pose.bones.get("head")
    
    r_shoulder.constraints.remove(r_shoulder.constraints[0])
    l_shoulder.constraints.remove(l_shoulder.constraints[0])
    spine_four.constraints.remove(spine_four.constraints[0])
    head.constraints.remove(head.constraints[0])
    
    target.pose.bones["neck"].constraints["Copy Location"].influence = 0.5
    
    hips = target.pose.bones.get("hips")
    hips.location = (0, 0.07, 0)
    hips.keyframe_insert(data_path="location", frame=bpy.data.scenes[0].frame_start)
    
    target.select_set(True)
    
    bpy.context.view_layer.objects.active = target

    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.nla.bake(frame_start=bpy.data.scenes[0].frame_start, frame_end=bpy.data.scenes[0].frame_end, visual_keying=True, bake_types={'POSE'})
    bpy.ops.object.mode_set(mode='OBJECT')
    
    target.select_set(False)
    
    delete_constraints(target)
    
     
def smooth_animation(armature):
    
    context = bpy.context
    scene = context.scene
    mytool = scene.settings
    
    armature = scene.objects.get(mytool.eyedropper)
    
    bpy.data.objects["Body"].select_set(True)
    bpy.data.objects["Pose"].select_set(True)
    
    if (mytool.smooth_val > 0.00):
        new_drivers = body_names
                    
        for n in range(31):
            new_drivers = bpy.data.objects[body_names[n]]
            new_drivers.select_set(True)
            bpy.context.view_layer.objects.active = new_drivers
            fcurves = bpy.context.active_object.animation_data.action.fcurves
            bpy.context.area.type = "GRAPH_EDITOR"
            bpy.ops.graph.gaussian_smooth(factor=((mytool.smooth_val)/10))
            new_drivers.select_set(False)
        
        #bpy.data.objects[mytool.eyedropper].data.bones["lip.B"].select = True
        #bpy.data.objects[mytool.eyedropper].data.bones["lip.T"].select = True
        
        #fcurves = bpy.context.active_object.animation_data.action.fcurves
        #bpy.context.area.type = "GRAPH_EDITOR"
        #bpy.ops.graph.gaussian_smooth(factor=((mytool.smooth_val)/10))

        #bpy.data.objects[mytool.eyedropper].data.bones["lip.B"].select = False
        #bpy.data.objects[mytool.eyedropper].data.bones["lip.T"].select = False
        
        bpy.context.area.type = "VIEW_3D"
        scene = context.scene
        mytool = scene.settings
                        
        selected_armature = scene.objects.get(mytool.eyedropper)
                        
        selected_armature.select_set(False)
        bpy.data.objects["Body"].select_set(False)
        bpy.data.objects["Pose"].select_set(False)
            
        #fcurves = bpy.context.active_object.animation_data.action.fcurves
        #for curve in fcurves:
            #bpy.ops.graph.gaussian_smooth(factor=((mytool.scale_val)/10))
            
            
            
def save_animation(armature):
    
    context = bpy.context
    scene = context.scene
    mytool = scene.settings
    
    armature = scene.objects.get(mytool.eyedropper)
    object_armature = mytool.eyedropper
    
    armature.select_set(True)
    
    bpy.context.view_layer.objects.active = armature
    
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.nla.bake(frame_start=bpy.data.scenes[0].frame_start, frame_end=bpy.data.scenes[0].frame_end, visual_keying=True, bake_types={'POSE'})
    bpy.ops.object.mode_set(mode='OBJECT')
    
    armature.select_set(False)


        
        
def add_constraints(selected_armature):
    
    context = bpy.context
    scene = context.scene
    mytool = scene.settings
    
    selected_armature = scene.objects.get(mytool.eyedropper)
    
    constraint_bones = [
    "hand_ik.R",
    "hand_ik.L",
    "torso",
    "foot_ik.L",
    "foot_ik.R",
    "root",
    ]
    
    
    constraint_cubes = [
    "15 left wrist",
    "16 right wrist",
    "23 left hip",
    "32 right foot index",
    "31 left foot index",
    "24 right hip",
    ]
    
    
    
    for k in range(6):
        current_bone = constraint_bones[k]
        new_bone = selected_armature.pose.bones.get(current_bone)
        
        clc = new_bone.constraints.new("COPY_LOCATION")
        constraint_cubes_object = scene.objects.get(constraint_cubes[k])
        clc.target = constraint_cubes_object
        
    face_bone_constraint = selected_armature.pose.bones.get("head")
    crc = face_bone_constraint.constraints.new("COPY_ROTATION")
    constraint_cubes_object = scene.objects.get("00 nose")
    crc.target = constraint_cubes_object
    
    torso_bone_constraint = selected_armature.pose.bones.get("torso")
    crc_1 = torso_bone_constraint.constraints.new("COPY_ROTATION")
    constraint_cubes_object_1 = scene.objects.get("23 left hip")
    crc_1.target = constraint_cubes_object_1
    
    r = selected_armature.pose.bones.get("hand_ik.R")
    crc_2 = r.constraints.new("COPY_ROTATION")
    constraint_cubes_object_2 = scene.objects.get("Right Hand")
    crc_2.target = constraint_cubes_object_2
    
    l = selected_armature.pose.bones.get("hand_ik.L")
    crc_3 = l.constraints.new("COPY_ROTATION")
    constraint_cubes_object_3 = scene.objects.get("Left Hand")
    crc_3.target = constraint_cubes_object_3
    
    hip = selected_armature.pose.bones.get("spine_fk.002")
    crc_4 = hip.constraints.new("COPY_ROTATION")
    constraint_cubes_object_4 = scene.objects.get("24 right hip")
    crc_4.target = constraint_cubes_object_4
    bpy.context.object.pose.bones["spine_fk.002"].constraints["Copy Rotation"].use_x = False

        
    
    

    
class TransferAnimation(bpy.types.Operator):
    """Transfer Animation"""
    bl_idname = "object.transfer_animation"
    bl_label = "Transfer Animation"
    
    def execute(self, context):
        scene = context.scene
        mytool = scene.settings
        add_constraints(mytool.eyedropper)
        delete_stretch()
        return {'FINISHED'}
    
    
class Link(bpy.types.Operator):
    """Link Animation"""
    bl_idname = "object.link_animation"
    bl_label = "Link Animation"
    
    def execute(self, context):
        scene = context.scene
        mytool = scene.settings
        link_rok(mytool.source, mytool.target)
        return {'FINISHED'}
    
    
class Retarget(bpy.types.Operator):
    """Retarget Animation"""
    bl_idname = "object.retarget_animation"
    bl_label = "Retarget Animation"
    
    def execute(self, context):
        scene = context.scene
        mytool = scene.settings
        retarget_rok(mytool.source, mytool.target)
        return {'FINISHED'}
    
class DeleteConstraints(bpy.types.Operator):
    """Delete Constraints"""
    bl_idname = "object.delete_constraints"
    bl_label = "Delete Constraints"
    
    def execute(self, context):
        scene = context.scene
        mytool = scene.settings
        delete_constraints(mytool.target)
        return {'FINISHED'}
    
class DeleteEmpties(bpy.types.Operator):
    """Delete Empties"""
    bl_idname = "object.delete_empties"
    bl_label = "Delete Empties"
    
    def execute(self, context):
        scene = context.scene
        mytool = scene.settings
        delete_empties()
        return {'FINISHED'}
    
    
    
class SelectSystem(bpy.types.Operator):
    """Select System"""
    bl_idname = "object.select_system"
    bl_label = "Select System"
    
    
    def execute(self, context):
        new_drivers = body_names
        
        for n in range(31):
            new_drivers = bpy.data.objects[body_names[n]]
            new_drivers.select_set(True)
            
        scene = context.scene
        mytool = scene.settings
            
        selected_armature = scene.objects.get(mytool.eyedropper)
            
        selected_armature.select_set(True)
        bpy.data.objects["Body"].select_set(True)
        bpy.data.objects["Pose"].select_set(True)
        return {'FINISHED'}
    
    
class Smooth_animation(bpy.types.Operator):
    """Smooth Animation"""
    bl_idname = "object.smooth_animation"
    bl_label = "Smooth Animation"
    
    def execute(self, context):
        scene = context.scene
        mytool = scene.settings
        smooth_animation(mytool.eyedropper)
        return {'FINISHED'}
    
    
class Save_Animation(bpy.types.Operator):
    """Save Animation"""
    bl_idname = "object.save_animation"
    bl_label = "Save Animation"
    
    def execute(self, context):
        scene = context.scene
        mytool = scene.settings
        save_animation(mytool.eyedropper)
        return {'FINISHED'}


_classes = [
    BlenderMocapPanel,
    RunOperator,
    RunOperator_Face,
    RunFileSelector,
    RunFileSelector_Face,
    AddArmature,
    TransferAnimation,
    SelectSystem,
    Smooth_animation,
    Save_Animation,
    Link,
    Retarget,
    DeleteConstraints,
    DeleteEmpties,
    Settings,
    MessageBox
]


def register():
    for c in _classes: register_class(c)
    bpy.types.Scene.settings = bpy.props.PointerProperty(type=Settings)
    


def unregister():
    for c in _classes: unregister_class(c)
    del bpy.types.Scene.settings


if __name__ == "__main__":
    register()