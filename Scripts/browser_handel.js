async function get_command(){
    while (true){
        try {
            const response = await fetch("http://127.0.0.1:8000/")
            const json = await response.json()

            const value = json.message

            if (value === "pause_play"){
                pause_play();
            }
            else if (value === "next"){
                next();
            }
            else if(value === "prev"){
                prev();
            }
        }
        catch(error){
            console.error(error)
            await new Promise(resolve => setTimeout(resolve,1000))
        }
    }
}

get_command();

function pause_play(){
    const button = document.querySelector("[aria-label='Play'], [aria-label='Pause']")

    if (button){
        button.click()
    }
}

function next(){
    const next_btn = document.querySelector("[aria-label='Next']")

    if (next_btn){
        next_btn.click()
    }
}

function prev(){
    const previous_btn = document.querySelector("[aria-label='Previous']")

    if (previous_btn){
        previous_btn.click()
    }
}