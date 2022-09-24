extends Control

onready var scoreText = get_node("MarginContainer/HBoxContainer/coin_count")
onready var coins = get_node("MarginContainer/HBoxContainer/collected_coins_lbl")
onready var endgame = get_node("endgame")
var init_count : int = 0
# Called when the node enters the scene tree for the first time.
func _ready():
	set_score_text(init_count)
	endgame.visible = false

func set_score_text(score):
	scoreText.text = str(score)
	
func end_game():
	scoreText.visible = false
	coins.visible = false
	
	endgame.visible = true
	
	# wait 3 seconts to quit the game
	yield(get_tree().create_timer(3), "timeout")
	get_tree().quit()
	
