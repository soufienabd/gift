"""Render two vertical Limo gift promo reels with Blender.

Usage:
  blender -b -P render_reels.py -- --output-dir exports

Blender must be installed. The script creates 5s and 8s MP4 files at 1080x1920/30fps.
"""
import argparse
import math
import os
import sys

import bpy
from mathutils import Vector

WIDTH, HEIGHT, FPS = 1080, 1920, 30


def material(name, color, metallic=0.0, roughness=0.3, emission=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*color, 1)
        bsdf.inputs["Emission Strength"].default_value = emission
    return mat


def cube(name, location, scale, mat, bevel=0.08):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("Soft bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return obj


def text_obj(body, name, z, size, mat):
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    curve.extrude = 0.008
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = (0, -1.5, z)
    obj.rotation_euler[0] = math.radians(90)
    obj.data.materials.append(mat)
    return obj


def point_light(name, location, color, power, size):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = power
    data.color = color
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector((0, 0, 4)) - obj.location).to_track_quat("-Z", "Y").to_euler()


def make_scene(seconds, output_path):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.materials, bpy.data.cameras, bpy.data.lights, bpy.data.curves, bpy.data.meshes):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)

    purple = material("Midnight plum", (0.025, 0.005, 0.09), metallic=0.25)
    gold = material("Limo gold", (1.0, 0.48, 0.015), metallic=0.78, roughness=0.2)
    bright_gold = material("Glow gold", (1.0, 0.7, 0.04), metallic=0.45, emission=0.7)
    magenta = material("Gift magenta", (0.62, 0.015, 0.85), metallic=0.45)
    white = material("Warm white", (1.0, 0.88, 0.65), emission=1.0)
    blue = material("Diamond blue", (0.12, 0.65, 1.0), metallic=0.8, roughness=0.12, emission=0.25)

    # Dark, glossy stage and a circular gold pedestal.
    cube("Backdrop", (0, 1.5, 4), (30, 0.3, 30), purple, 0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=2.7, depth=0.22, location=(0, 0, 1.25))
    pedestal = bpy.context.object
    pedestal.name = "Gold presentation pedestal"
    pedestal.data.materials.append(gold)
    bevel = pedestal.modifiers.new("Rounded rim", "BEVEL")
    bevel.width = 0.09
    bevel.segments = 4
    pedestal.modifiers.new("Pedestal normals", "WEIGHTED_NORMAL")

    # Hero gift box assembled from separate beveled 3D parts.
    hero = bpy.data.objects.new("Gift animation pivot", None)
    bpy.context.collection.objects.link(hero)
    hero.location = (0, 0, 4.25)
    parts = [
        cube("Gift box", (0, 0, 4.1), (2.35, 1.55, 1.75), magenta, 0.12),
        cube("Gift lid", (0, 0, 5.03), (2.55, 1.7, 0.34), gold, 0.08),
        cube("Vertical gold ribbon", (0, -0.79, 4.45), (0.34, 0.06, 1.55), bright_gold, 0.025),
        cube("Horizontal gold ribbon", (0, -0.8, 4.05), (2.25, 0.06, 0.27), bright_gold, 0.025),
        cube("Ribbon top", (0, -0.78, 5.25), (0.35, 0.07, 0.38), bright_gold, 0.06),
    ]
    for obj in parts:
        obj.parent = hero
        obj.matrix_parent_inverse = hero.matrix_world.inverted()

    # Crown above the gift: a gold band plus jewel-like points.
    bpy.ops.mesh.primitive_torus_add(major_radius=0.62, minor_radius=0.11, major_segments=48, minor_segments=12, location=(0, -0.1, 5.95))
    crown_band = bpy.context.object
    crown_band.name = "Crown band"
    crown_band.scale.z = 0.55
    crown_band.data.materials.append(gold)
    for i in range(5):
        x = (i - 2) * 0.28
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.16, radius2=0, depth=0.72, location=(x, -0.1, 6.25 + (0.15 if i % 2 else 0)))
        bpy.context.object.name = "Crown point"
        bpy.context.object.data.materials.append(bright_gold)
    # Floating diamond accents.
    for x, z in [(-2.0, 4.5), (2.0, 4.1), (-1.7, 6.3), (1.8, 6.4)]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.36, location=(x, -0.35, z))
        jewel = bpy.context.object
        jewel.name = "Floating blue gift jewel"
        jewel.scale = (0.8, 0.45, 1.15)
        jewel.data.materials.append(blue)

    # Title and French call to action, kept clear of the main 3D gift.
    text_obj("CADEAUX 3D", "Reel title", 7.65, 0.72, white)
    text_obj("LIMO  •  BATTLE  •  GIFTS", "Brand line", 7.02, 0.28, bright_gold)
    text_obj("Offrez un moment spectaculaire", "Call to action", 1.85, 0.31, white)
    text_obj("Des cadeaux qui font briller le live", "Tagline", 1.42, 0.22, bright_gold)

    # Decorative glowing particles.
    for i in range(22):
        angle = i * 2.399
        radius = 2.6 + (i % 4) * 0.28
        x = math.cos(angle) * radius
        z = 4.4 + math.sin(angle) * radius
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.045 + (i % 3) * 0.018, location=(x, -0.55, z))
        particle = bpy.context.object
        particle.name = "Golden sparkle"
        particle.data.materials.append(bright_gold)

    # Animate a gentle turn and scale pulse on the gift assembly.
    hero.rotation_euler[2] = math.radians(-8)
    hero.keyframe_insert(data_path="rotation_euler", frame=1)
    hero.keyframe_insert(data_path="location", frame=1)
    hero.rotation_euler[2] = math.radians(8)
    hero.location.z = 4.5
    hero.keyframe_insert(data_path="rotation_euler", frame=max(2, int(seconds * FPS / 2)))
    hero.keyframe_insert(data_path="location", frame=max(2, int(seconds * FPS / 2)))
    hero.rotation_euler[2] = math.radians(-8)
    hero.location.z = 4.25
    hero.keyframe_insert(data_path="rotation_euler", frame=seconds * FPS)
    hero.keyframe_insert(data_path="location", frame=seconds * FPS)
    for action in bpy.data.actions:
        for fcurve in action.fcurves:
            for key in fcurve.keyframe_points:
                key.interpolation = "BEZIER"

    point_light("Warm key", (4, -7, 9), (1.0, 0.55, 0.16), 1500, 6)
    point_light("Purple fill", (-5, -4, 5), (0.55, 0.12, 1.0), 1800, 5)
    point_light("Gold rim", (0, 4, 8), (1.0, 0.25, 0.025), 2200, 4)

    camera_data = bpy.data.cameras.new("Portrait camera")
    camera = bpy.data.objects.new("Portrait camera", camera_data)
    bpy.context.collection.objects.link(camera)
    camera.location = (0, -22, 4.5)
    camera.rotation_euler = (Vector((0, 0, 4.5)) - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = 52
    bpy.context.scene.camera = camera

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.eevee.taa_render_samples = 32
    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.render.resolution_percentage = 100
    scene.render.fps = FPS
    scene.frame_start = 1
    scene.frame_end = seconds * FPS
    scene.world.color = (0.008, 0.001, 0.025)
    scene.view_settings.view_transform = "AgX"
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "HIGH"
    scene.render.filepath = output_path
    scene.frame_set(1)
    bpy.ops.render.render(animation=True)


def main():
    args_list = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description="Render vertical 3D gift promo reels")
    parser.add_argument("--output-dir", default="exports")
    args = parser.parse_args(args_list)
    os.makedirs(args.output_dir, exist_ok=True)
    for seconds in (5, 8):
        path = os.path.abspath(os.path.join(args.output_dir, f"limo-cadeaux-{seconds}s.mp4"))
        print(f"Rendering {path}")
        make_scene(seconds, path)
    print("Done: 5-second and 8-second MP4 reels rendered.")


if __name__ == "__main__":
    main()
