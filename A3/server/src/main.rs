mod api;

use api::{
    index,
    sum,
    subtract,
    multiply,
    divide
};

use actix_web::{HttpServer, App, middleware::Logger};

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Just for logging
    std::env::set_var("RUST_LOG", "debug");
    std::env::set_var("RUST_BACKTRAC", "1");
    env_logger::init();

    HttpServer::new(move || {
        let logger = Logger::default();

        App::new()
        .wrap(logger)
        .service(index)
        .service(sum)
        .service(subtract)
        .service(multiply)
        .service(divide)
    })
    .bind(("127.0.0.1", 8000))?
    .run()
    .await
}
