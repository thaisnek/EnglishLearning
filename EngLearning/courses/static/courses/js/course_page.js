var player;
document.onreadystatechange = function (){
    if(document.readyState == 'interactive'){
        player = document.getElementById('player')
        lesson_list = document.getElementById("lesson_list")
        mentainRatio()
    }
}

function mentainRatio(){
    var w = player.clientWidth
    var h = (w*9)/16
    console.log({w,h});
    player.height = h
    lesson_list.style.maxHeight = h + "px"
}

window.onresized = mentainRatio

function toggleVideos(lessonId) {
    var videoList = document.getElementById('videos-' + lessonId);
    if (videoList.style.display === "none") {
        videoList.style.display = "block";
    } else {
        videoList.style.display = "none";
    }
}

document.querySelectorAll('.collapse-accordion-toggle').forEach(button => {
    button.addEventListener('click', function() {
        const plusIcons = button.querySelectorAll('.plus-icon');
        const minusIcons = button.querySelectorAll('.minus-icon');

        plusIcons.forEach(icon => icon.style.display = icon.style.display === 'none' ? 'block' : 'none');
        minusIcons.forEach(icon => icon.style.display = icon.style.display === 'none' ? 'block' : 'none');
    });
});


