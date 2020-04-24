"""Provides a scripting component.
    Inputs:
        boundary_curve: boundary curve input
        top_surface: top surface imput
        bottom_surface: bottom surface imput
        distance_x: separation x axis
        distance_y: separation y axis
        count_x: # of items in x axis
        count_y: # of items in y axis
        block_w: width blocks
        block_d: width depth
        random_seed: int number for random seed
        max_probability: for cull elements near boundary line
        max_tilt: range of tilt
    Output:
        bottom_pts: Points on base 
        planes: Planes on base
        Solids: Concrete blocks
        
    Based on Jose Luis Garcia del Castillo Tutorial:
        https://www.youtube.com/watch?v=eRfgAdOze_A
        Computational Design Live Stream #02
        Berlin Holocaust Memorial monument: creating the 
        full model using C# scripting only!
        
"""

__author__ = "Ivan Perez | joseivanperezdiaz1@gmail.com | Bogotá | Colombia"

import rhinoscriptsyntax as rs
import Grasshopper.Kernel as gh
import random
import math
import Rhino.Geometry as rg

e = gh.GH_RuntimeMessageLevel.Error
w = gh.GH_RuntimeMessageLevel.Warning

#Generate grid of points
base_points = []
for i in range(0,count_x):
    i += i
    for j in range (0, count_y):
        j += j
        x = distance_x * i
        y = distance_y * j
        p = rs.AddPoint(x, y, 0)
        base_points.append(p)
 

# Cull points outside curve
culled_pts = []
  
if rs.IsCurveClosed(boundary_curve) and rs.IsCurvePlanar(boundary_curve): # Checking curve is ok
    for i in base_points:
        if i:
            result = rs.PointInPlanarClosedCurve(i, boundary_curve)
            if result==0:
                pass
                #print ('The point is outside of the closed curve.')
            elif result==1:
                #print('The point is inside of the closed curve.')
                culled_pts.append(i)
                
else:
    ghenv.Component.AddRuntimeMessage(e, 'The curve must be planar and closed')



# Cull closest points of curve
rndm_cull_points = []

for i in culled_pts:
    rndm_number = random.uniform(0, max_probability)
    random.seed = random_seed
    param = rs.CurveClosestPoint(boundary_curve, i)
    pt = rs.EvaluateCurve(boundary_curve, param)
    # rndm_cull_points.append(pt)
    distance = rs.Distance(pt, i)
    invert_distance = 1.0 / distance
    # print(str(distance) + str(invert_distance) + ' r: ' + str(rndm_number))
    
    if invert_distance < rndm_number:
        rndm_cull_points.append(i)


# Project points to bottom surface
btm_surface = [bottom_surface] # Create a list with one single element
bottom_pts = rs.ProjectPointToSurface(rndm_cull_points, btm_surface, (0,0,-1))


# Project points to top surface
top_surface = [top_surface] # Create a list with one single element
top_pts = rs.ProjectPointToSurface(rndm_cull_points, top_surface, (0,0,1))


# Planes on the bottom
bottom_planes = []
for i in bottom_pts:
    view = rs.CurrentView()
    planes = rs.CreatePlane(i, (1,0,0), (0,1,0))
    bottom_planes.append(planes)
  
    
# Rotate planes on ZAxis
rotated_planes = []
for i in bottom_planes:
    plane = rs.ViewCPlane()
    rndm_angle = random.randrange(-5, 5) 
    rotated_z = rs.RotatePlane(i, rndm_angle, planes.ZAxis)
    # Tilt control
    tilt = random.randrange(-5, 5) * max_tilt
    rotated_x = rs.RotatePlane(rotated_z, tilt, planes.XAxis)
    rotated_planes.append(rotated_x)
    
    
# Create solids
solids = []
for j in range(0, len(rotated_planes)):
    line = rs.AddLine(bottom_pts[j], top_pts[j])
    rct = rs.AddRectangle( rotated_planes[j], 
    rg.Interval(-0.5 * block_w, 0.5 * block_w), 
    rg.Interval(-0.5 * block_d, 0.5 * block_d))
    solid = rs.ExtrudeCurve(rct, line)
    sld = rs.CapPlanarHoles(solid)
    solids.append(solid)
    
print('Ivan Perez | joseivanperezdiaz1@gmail.com | Bogotá | Colombia')