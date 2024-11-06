const lecture_id = window.location.search;
const find="[href='"+lecture_id+"']";
var elm = document.querySelector(find);
for(var i=0;i<5;i++){
    if(elm==null) break;
    elm=elm.parentElement;
    if(i<4) elm.style.backgroundColor="aliceblue";
    if(i==4) elm.className="collapse show";
}
const col3=document.getElementsByClassName("col-3")[0];
const links = col3.querySelectorAll("a");
links.forEach(link=>{
    var elm=link;
    for(var i=0;i<4;i++){
        if(elm==null) break;
        elm=elm.parentElement;
        elm.addEventListener("click",function(){
            window.location.href=link.href;
        })
    }
});

const scroll=document.getElementById("lesson_list");
const rfHeight=document.getElementsByClassName('col')[0].children;
function updateScrollBar() {
    scroll.style= "overflow-y:auto";
    scroll.style.height=rfHeight[0].clientHeight+rfHeight[1].clientHeight + "px";
}
window.onload = updateScrollBar;
window.addEventListener('resize', updateScrollBar);
