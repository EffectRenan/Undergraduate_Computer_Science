use actix_web::{
    get,
    web::Path,
};

use serde::{Serialize, Deserialize};

#[derive(Deserialize, Serialize)]
pub struct Operands {
    operand1: f32,
    operand2: f32
}

#[get("/sum/{operand1}/{operand2}")]
pub async fn sum(operands: Path<Operands>) -> String {
    let ops = operands.into_inner();
    return String::from(format!("{}", (ops.operand1 + ops.operand2)));
}

#[get("/subtract/{operand1}/{operand2}")]
pub async fn subtract(operands: Path<Operands>) -> String {
    let ops = operands.into_inner();
    return String::from(format!("{}", (ops.operand1 - ops.operand2)));
}

#[get("/multiply/{operand1}/{operand2}")]
pub async fn multiply(operands: Path<Operands>) -> String {
    let ops = operands.into_inner();
    return String::from(format!("{}", (ops.operand1 * ops.operand2)));
}

#[get("/divide/{operand1}/{operand2}")]
pub async fn divide(operands: Path<Operands>) -> String {
    let ops = operands.into_inner();
    return String::from(format!("{}", (ops.operand1 / ops.operand2)));
}

#[get("/")]
pub async fn index() -> String {
    let resp = "
Sample: /<operator>/operand1/operand2
        /sum/2/1

Operators:
    sum
    subtract
    multiply
    divide
";

    return String::from(resp);
}
