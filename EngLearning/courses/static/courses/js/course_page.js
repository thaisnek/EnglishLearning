var player;
var lesson_list;
var card;

document.onreadystatechange = function () {
    if (document.readyState == 'interactive') {
        player = document.getElementById('player');
        lesson_list = document.getElementById("lesson_list");
        card = document.querySelector(".card.p-3");
        maintainRatio();
        adjustLessonListHeight();
    }
};

function maintainRatio() {
    var w = player.clientWidth;
    var h = (w * 9) / 16;
    console.log({ w, h });
    player.height = h;
}

function adjustLessonListHeight() {
    if (card && lesson_list) {
        lesson_list.style.maxHeight = `${card.clientHeight}px`;
    }
}

window.onresize = function () {
    maintainRatio();
    adjustLessonListHeight();
};
