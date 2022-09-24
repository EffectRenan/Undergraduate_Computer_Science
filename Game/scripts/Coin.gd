extends Area

export var value = 1

func _ready():
	pass

func _physics_process(delta):
	rotate_y(deg2rad(3))

func _on_Coin_body_entered(body):
	# was it the player?
	if body.name == "Player":
		body.collect_coin(value)
		queue_free()
