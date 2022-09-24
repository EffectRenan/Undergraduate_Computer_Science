#![crate_name = "producer"]

use std::thread;
use std::time::Duration;
use rand::Rng;

fn main() {
    println!("Connecting to the server...");

    let context = zmq::Context::new();
    let requester = context.socket(zmq::REQ).unwrap();
    let mut msg = zmq::Message::new();

    assert!(requester.connect("tcp://localhost:5555").is_ok());
   
    // The available foods and drinks in these vectors contain invalid options of the menu to test
    let foods: Vec<&str> = vec!["beef", "pizza", "strogonoff", "hamburguer", "fries", "tomato", "salsa"];
    let drinks: Vec<&str> = vec!["juice", "soda", "beer", "wine", "water", "coffee", "milkshake"];

    let mut rng = rand::thread_rng();
    loop {

        // Food
        if rng.gen_range(0..2) == 0 {
            let item = rng.gen_range(0..foods.len());
            println!("Trying to produce a {}... ", foods[item]);
            requester.send(format!("producer food {}", foods[item]).as_str(), 0).unwrap();


        // Drink
        } else {
            let item = rng.gen_range(0..drinks.len());
            println!("Trying to produce a {}... ", drinks[item]);
            requester.send(format!("producer drink {}", drinks[item]).as_str(), 0).unwrap();
        }
        
        requester.recv(&mut msg, 0).unwrap();
        println!("Received: {}", msg.as_str().unwrap());
       
        // Waiting time to produce another one
        thread::sleep(Duration::from_millis(2000));
    }
}
