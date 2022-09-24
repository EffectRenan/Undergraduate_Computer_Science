#![crate_name = "server"]

use std::collections::VecDeque;
use std::thread;
use std::time::Duration;

fn main() {

    let mut foods_queue: VecDeque<String> = VecDeque::new();
    let mut drinks_queue: VecDeque<String> = VecDeque::new();

    // ZeroMQ.
    let context = zmq::Context::new();
    let responder = context.socket(zmq::REP).unwrap();
    assert!(responder.bind("tcp://*:5555").is_ok());

    println!("Server listening on port 5555 ...");

    let foods_menu: Vec<&str> = vec!["beef", "pizza", "strogonoff", "hamburguer", "fries"];
    let drinks_menu: Vec<&str> = vec!["juice", "soda", "beer", "wine", "water"];

    let mut msg = zmq::Message::new();

    loop {
        responder.recv(&mut msg, 0).unwrap();

        let splitted: Vec<String> = msg.as_str().unwrap().split_whitespace().map(|s| s.to_string()).collect();

        if splitted.len() < 2 || splitted.len() > 3 {
            responder.send("bad format: <producer/consumer> <food/drink> <item>", 0).unwrap();
            continue;
        }

        match splitted[0].as_str() {
            "producer" => {
                println!("Received producer request");

                match splitted[1].as_str() {
                    "food" => {
                        if foods_menu.contains(&splitted[2].as_str()) {
                            foods_queue.push_back(splitted[2].to_owned());
                            responder.send("good", 0).unwrap();
                        } else {
                            responder.send("bad item", 0).unwrap();
                        }
                    },

                    "drink" => {
                        if drinks_menu.contains(&splitted[2].as_str()) {
                            drinks_queue.push_back(splitted[2].to_owned());
                            responder.send("good", 0).unwrap();
                        } else {
                            responder.send("bad item", 0).unwrap();
                        }

                    }
                    _ => {
                        responder.send("bad <food/drink>", 0).unwrap();
                    }

                }
            },

            "consumer" => {
                println!("Received consumer request");

                match splitted[1].as_str() {
                    "food" => {
                        if !foods_queue.is_empty() {
                            responder.send(foods_queue.pop_front().unwrap().as_str(), 0).unwrap();
                        } else {
                            responder.send("bad", 0).unwrap();
                        }
                    },

                    "drink" => {
                        if !drinks_queue.is_empty() {
                            responder.send(drinks_queue.pop_front().unwrap().as_str(), 0).unwrap();
                        } else {
                            responder.send("bad", 0).unwrap();
                        }
                    }
                    _ => {
                        responder.send("bad", 0).unwrap();
                    }
                }
            },
            _ => {
                responder.send("bad", 0).unwrap();
            }

        }

        println!("Foods queue: {}", foods_queue.len());
        println!("Drinks queue: {}", drinks_queue.len());
        thread::sleep(Duration::from_millis(1000));
    }
}

