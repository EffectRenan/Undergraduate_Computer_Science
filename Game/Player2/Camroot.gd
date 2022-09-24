extends Spatial

var camrot_h = 0
var camrot_v = 0
var cam_v_max = 75
var cam_v_min = -55
var h_sensitivity = 0.1
var v_sensitivity = 0.1
var h_acceleration = 10
var v_acceleration = 10

func _ready():
	# Hide the cursor
	Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
	
	# Camera does not colide with the player
	$h/v/Camera.add_exception(get_parent())
	
func _input(event):
	
	# Increase the value of h or v
	if event is InputEventMouseMotion:
		camrot_h += -event.relative.x * h_sensitivity
		camrot_v += event.relative.y * v_sensitivity
		
func _physics_process(delta):
	
	# Test min and max in vertical
	camrot_v = clamp(camrot_v, cam_v_min, cam_v_max)
	
	# Set the rotation based on h and v with linear interpolation
	$h.rotation_degrees.y = lerp($h.rotation_degrees.y, camrot_h, delta * h_acceleration)
	$h/v.rotation_degrees.x = lerp($h/v.rotation_degrees.x, camrot_v, delta * v_acceleration)
	
