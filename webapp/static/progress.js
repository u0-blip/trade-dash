
function start_long_task() {
    // add task status elements
    div = $('<div class="progress"><p></p><p>0%</p><div>...</div><div>&nbsp;</div></div><hr>');
    $('#progress').append(div);

    // create a progress bar
    var nanobar = new Nanobar({
        bg: '#44f',
        target: div[0].childNodes[0]
    });

    // send ajax POST request to start background job
    $.ajax({
        type: 'POST',
        url: '/longtask',
        success: function (data, status, request) {
            status_url = request.getResponseHeader('Location');
            update_progress(status_url, nanobar, div[0]);
        },
        error: function () {
            alert('Unexpected error');
        }
    });
}
function show_image(){
    var RMS_img = document.getElementById('RMS-image')
    RMS_img.src = window.location.origin  + '/sim_image_data'
}

function update_progress(status_url, nanobar, status_div) {
    // send GET request to status URL
    $.getJSON(status_url, function (data) {
        // update UI
        console.log(data)
        percent = parseInt(data['current'] * 100 / data['total']);
        nanobar.go(percent);

        var elem = document.getElementById("myBar");

        elem.style.width = percent + "%";
        elem.innerHTML = percent + "%";

        $(status_div.childNodes[1]).text(data['current'] + ' of ' + data['total'] + ' is done. ');
        $(status_div.childNodes[2]).text(data['status']);

        if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
            if ('result' in data) {
                // show result
                $(status_div.childNodes[3]).text('Result: ' + data['result']);
                show_image()
            }
            else {
                // something unexpected happened
                $(status_div.childNodes[3]).text('Result: ' + data['state']);
            }
        }
        else {
            // rerun in 2 seconds
            setTimeout(function () {
                update_progress(status_url, nanobar, status_div);
            }, 2000);
        }
    });
}

$(function () {
    $('#start-bg-job').click(start_long_task);
});


function download_res(){
    var download_btn = document.getElementById('my_iframe')
    download_btn.src = window.location.origin  + '/result'
}

$(function () {
    $('#download-file').click(download_res);
});


function image_tab(imgs) {
    // Get the expanded image
    var expandImg = document.getElementById("expandedImg");
    // Get the image text
    var imgText = document.getElementById("imgtext");
    // Use the same src in the expanded image as the image being clicked on from the grid
    expandImg.src = imgs.src;
    // Use the value of the alt attribute of the clickable image as text inside the expanded image
    imgText.innerHTML = imgs.alt;
    // Show the container element (hidden with CSS)
    expandImg.parentElement.style.display = "block";
}