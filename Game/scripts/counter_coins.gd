extends Label

var init_count = 0

func _ready():
	text=String(init_count)
	
func set_score_text(score):
	text = str(score)
