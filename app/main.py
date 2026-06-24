
import json
from fastapi import FastAPI,HTTPException #api
from database import get_connection #for postgresql db connection
from cache import redis_client #for redis

app=FastAPI()

conn=get_connection() #establishing connection
cursor=conn.cursor()
    
cursor.execute("CREATE TABLE IF NOT EXISTS students (roll_number int primary key, name varchar(100) NOT NULL,age int NOT NULL)")
    
conn.commit()
cursor.close()
conn.close()

@app.get("/health")
def health_check():
    return {"status":"ok"}

@app.get("/student/{roll_number}")
def get_student(roll_number: int):
    cached=redis_client.get(f"student:{roll_number}")
    if cached:
        return {**json.loads(cached),"source":"cache"} #converting txt to dictionary **unpacks dict cache is o/p of redis and source is our keyword
    
    conn=get_connection() #establishing connection
    cursor=conn.cursor()
    
    cursor.execute("SELECT roll_number,name,age FROM students WHERE roll_number=%s",(roll_number,))
    
    row=cursor.fetchone() #closing connection
    cursor.close()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404,detail="student not found")
    data={"roll_number":row[0],"name":row[1],"age":row[2]}
    redis_client.set(f"student:{roll_number}",json.dumps(data),ex=60) #o/p is dictionary so converting to txt as redis only stores strings/bytes
    return {**data,"source":"db"} #adding to the data so that we can know from we got the data

@app.post("/students")
def create_student(roll_number: int,name: str,age: int ):
    conn=get_connection() #establishing connection
    cursor=conn.cursor()
    
    cursor.execute("INSERT into students(roll_number,name,age)VALUES(%s,%s,%s)",(roll_number,name,age),)
    
    conn.commit() 
    #closing connection
    cursor.close()
    conn.close()
    return {"message":"student created"}
