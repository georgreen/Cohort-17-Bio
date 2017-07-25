console.log("linked")

let url = window.location.href;

function get_data()
{
    endpoint = url.slice(0, url.lastIndexOf("/")) + "/totalusers";
    const requestObj = new XMLHttpRequest();
    requestObj.open('GET', endpoint, true);
    requestObj.send()
    requestObj.onreadystatechange = processdata;

    function processdata(e)
    {
        if (requestObj.readyState == 4 && requestObj.status == 200)
        {
            const data = JSON.parse(requestObj.responseText);
            console.log(data['total']);
            $(".counter").html("<div class=' counter counter-style col-md-12'>" + data['total'] + "</div>")
        }
    }
}

get_data();
