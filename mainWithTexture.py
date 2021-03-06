"""Affichage de simulation d'aiguille dans différents matériaux
Ce module permet d'afficher le déplacement 1D d'une aiguille
"""
import math
from glumpy import app, gloo, gl, glm, data

MUR = [-0.5, 0, 0.5]
OLDMUR = {MUR[0]: 0, MUR[1]: 0, MUR[2]: 0}

#####################################################################################################

VERTEX = """
  uniform float scale;
  attribute vec2 position;
  attribute vec4 color;
  varying vec4 v_color;
  void main()
  {
    gl_Position = vec4(scale*position, 0.0, 1.0);
    v_color = color;
  } """

VERTEXM = """
  uniform float depla;
  uniform float scale;
  attribute vec2 position;
  attribute vec4 color;
  varying vec4 v_color;
  void main()
  {
    gl_Position = vec4(scale*position, 0.0, 1.0);
    v_color = color;
  } """

FRAGMENT = """
  varying vec4 v_color;    // Interpolated fragment color (in)
  void main()
  {
      gl_FragColor = v_color;
  } """

# Pour les Textures #
##################################################################################
VERTEXS = """
  attribute vec2 a_position;      // Vertex position
  attribute vec2 a_texcoord;      // Vertex texture coordinates
  varying vec2   v_texcoord;      // Interpolated fragment texture coordinates (out)
  void main()
  {
    // Assign varying variables
    v_texcoord  = a_texcoord;
    // Final position
    gl_Position = vec4(a_position,1.0);
  } 
  """

FRAGMENTS= """
  uniform sampler2D texture;  // Texture 
  varying vec2      v_texcoord; // Interpolated fragment texture coordinates (in)
  void main()
  {
    // Get texture color
    gl_FragColor = texture2D(texture, v_texcoord);
    // Final color
    //gl_FragColor = t_color;
  }"""
##################################################################################


#####################################################################################################

# Build the program and corresponding buffers (with 4 vertices)
FOND = gloo.Program(VERTEX, FRAGMENT, count=4)



# Upload data into GPU
FOND['color'] = [(1, 1, 1, 1)] * 4
FOND['position'] = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
FOND['scale'] = 1.0

AIGUILLE = gloo.Program(VERTEXM, FRAGMENT, count=4)
AIGUILLE['color'] = [(0.5, 0.5, 0.5, 1), (1, 1, 1, 1), (0, 0, 0, 1), (1, 1, 1, 1)]
AIGUILLE['position'] = [(-4, -0.05), (-4, +0), (-0.6, -0.05), (-0.5, +0)]
AIGUILLE['scale'] = 1.0
AIGUILLE["depla"] = 0.0

def sticky(pos_mur, pos_aig):
    """
    Compare la position du mur et de l'aiguille et retourne la déformation
    """
    dif = pos_aig-pos_mur
    posi = 0
    if OLDMUR[pos_mur] == 1:
        if dif < -0.1:
            posi = 0
            OLDMUR[pos_mur] = 0
        elif dif-0.1 < 0:
            posi = dif-0.1
    else:
        if dif > 0.1:
            posi = 0
            OLDMUR[pos_mur] = 1
        elif dif > 0:
            posi = dif
    return posi

def posmur(pos_mur, pos_aig=0):
    """
    retourne la liste correspondant aux coordonnées des triangles du mur
    """
    return [(pos_mur, -0.25), (pos_mur, -1), (pos_mur+sticky(pos_mur, pos_aig), -0), (+1, -1),\
     (+1, +1), (pos_mur+sticky(pos_mur, pos_aig), -0), (pos_mur, 1), (pos_mur, +0.25)]

MUR1 = gloo.Program(VERTEXS, FRAGMENTS, count=8)
MUR1['texture'] = data.get("eau.png")
MUR1['position'] = posmur(MUR[0])
MUR1['scale'] = 1

MUR2 = gloo.Program(VERTEX, FRAGMENT, count=8)
MUR2['color'] = [(1, 1, 0, 1)] * 8
MUR2['position'] = posmur(MUR[1])
MUR2['scale'] = 1

MUR3 = gloo.Program(VERTEX, FRAGMENT, count=8)
MUR3['color'] = [(0, 0, 1, 1)] * 8
MUR3['position'] = posmur(MUR[2])
MUR3['scale'] = 1


#####################################################################################################
# Create a window with a valid GL context
WINDOW = app.Window(800, 600)
#Calcul des parois molles

# Tell glumpy what needs to be done at each redraw
@WINDOW.event

def on_draw(dtemps):
    """
    Ce qui se passe à chaque raffraichissement
    """
    WINDOW.clear()
    FOND.draw(gl.GL_TRIANGLE_STRIP)
    AIGUILLE["depla"] += dtemps
    depla = math.sin(AIGUILLE["depla"])
    MUR1['position'] = posmur(MUR[0], depla)
    MUR1.draw(gl.GL_TRIANGLE_STRIP)
    MUR2['position'] = posmur(MUR[1], depla)
    MUR2.draw(gl.GL_TRIANGLE_STRIP)
    MUR3['position'] = posmur(MUR[2], depla)
    MUR3.draw(gl.GL_TRIANGLE_STRIP)

    AIGUILLE['position'] = [(-4, -0.05), (-4, +0), (-0.6+depla+0.5, -0.05), (-0.5+depla+0.5, +0)]
    AIGUILLE.draw(gl.GL_TRIANGLE_STRIP)

# Run the app
app.run()
