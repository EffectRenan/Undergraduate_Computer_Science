#![crate_name = "consumer"]

use std::thread;
use std::time::Duration;
use rand::Rng;

fn main() {
    println!("Connecting ...");

    let context = zmq::Context::new();
    let requester = context.socket(zmq::REQ).unwrap();
    let mut msg = zmq::Message::new();

    assert!(requester.connect("tcp://localhost:5555").is_ok());
    println!("Connected!");

    let mut rng = rand::thread_rng();
    loop {
        if rng.gen_range(0..2) == 0 {
            println!("Checking if a drink is available ...");
            requester.send("consumer drink", 0).unwrap();

        } else {
            println!("Checking if a food is available ...");
            requester.send("consumer food", 0).unwrap();
        }
        
        requester.recv(&mut msg, 0).unwrap();
        
        if msg.as_str().unwrap() == "bad" {
            println!("No item available!");

            // Waiting time to try again
            thread::sleep(Duration::from_millis(1000));
        } else {
            println!("Delivering: {} ...", msg.as_str().unwrap());

            // Time to simulate the delivery: 3-5 secs
            thread::sleep(Duration::from_millis(rng.gen_range(3000..5000)));
            println!("Delivered!");
        }

    }
}

