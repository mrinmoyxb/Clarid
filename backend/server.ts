import app from "./app.ts"

if(!process.env.PORT){
    console.log("MISSING PORT");
}

const PORT = Number(process.env.PORT);

app.listen(PORT, ()=>{
    console.log(`Server is running on PORT: ${PORT}`);
})