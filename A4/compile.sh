#!/bin/sh

cd server 
cargo clean
cargo build
cd ..

cd producer 
cargo clean
cargo build
cd ..

cd consumer
cargo clean
cargo build
cd ..

# ---

if [[ $(ls | grep 'bin') == '' ]]; then
    mkdir bin
else 
    rm ./bin/*
fi

cp ./server/target/debug/server ./bin/server
cp ./producer/target/debug/producer ./bin/producer
cp ./consumer/target/debug/consumer ./bin/consumer

clear

echo "Check ./bin out"
