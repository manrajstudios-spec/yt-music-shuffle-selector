async function get_command(){
    while (true){
        try {
            const response = await fetch("http://127.0.0.1:8000/action")
            const json = await response.json()

            const value = json.message

            if (value === "play_pause"){
                pause_play();
            }
            else if (value === "next"){
                next();
            }
            else if(value === "prev"){
                prev();
            }

            await new Promise(resolve => setTimeout(resolve,2000))

            await fetch("http://127.0.0.1:8000/action_done")
        }
        catch(error){
            console.error(error)
            await new Promise(resolve => setTimeout(resolve,1000))
        }
    }
}

get_command();

function pause_play() {
    const main_btn = document.querySelector('ytmusic-play-button-renderer[aria-label="Play temp"]');

    if (main_btn){
        main_btn_state = main_btn.getAttribute("state");

        console.log(main_btn_state);

        if (main_btn_state === "default"){
            console.log("state default")
            main_btn.click();
        }
        else{
            const player_btn = document.getElementById("play-pause-button");

            if (player_btn){
                console.log("btn found")
                player_btn.click();
            }
            else{
                console.log("btn not found")
            }
        }
    }
    else{
        console.log("main_btn null")
        const player_btn = document.getElementById("play-pause-button");
         if (player_btn){
             console.log("btn found")
             player_btn.click();
         }
         else{
             console.log("btn not found")
         }
    }
}

function next(){
    const next_btn = document.querySelector("ytmusic-player-bar [aria-label='Next']")

    if (next_btn){
        next_btn.click()
    }
}

function prev(){
    const previous_btn = document.querySelector("ytmusic-player-bar [aria-label='Previous']")

    if (previous_btn){
        previous_btn.click()
    }
}