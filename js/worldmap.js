// This function is used to make XHR request to the backend, load data from the database
function doXHRRequest(url){
    
	var xhr = new XMLHttpRequest(); // simplified for clarity

    xhr.open("GET", url, false); // sending as POST, we give the argument "false" so the function waits for a return

	response =  [];
	i = 0;

    xhr.onreadystatechange = function() { //Call a function when the state changes.
        if(xhr.readyState == 4 && xhr.status == 200) { // complete and no errors
            response[i] = JSON.parse(xhr.responseText); // We do this in case of multiple xhr response, we store all of them in an array
			i++;
		}
    };

    xhr.send();
    return(response);
}

// We get the data from backend
countryMatchFrontBack = doXHRRequest("scriptAndDatabase/loadBackendData/getCountryCorrespondBackFront.php");
matchCountryRegion = doXHRRequest("scriptAndDatabase/loadBackendData/getCountryToRegionData.php");
totalPackages = doXHRRequest("scriptAndDatabase/loadBackendData/getTotalPackagesProcessed.php");
contributionGlobalStats = doXHRRequest("scriptAndDatabase/loadBackendData/getAverageCountryContribution.php");
averageContributionsByCountry = contributionGlobalStats[0];


// Simulated data - top package per region
var bestPackagesByRegion = {
    "North America": {
        "United States": {
            "package": "AwesomePackage",
            "size": 50
        },
        "Canada": {
            "package": "CoolPackage",
            "size": 30
        }
    },
    "Europe": {
        "Germany": {
            "package": "GreatPackage",
            "size": 25
        },
        "United Kingdom": {
            "package": "SuperPackage",
            "total commits": 20
        }
    }
};



// Update global statistics on the page
document.getElementById('total-packages').textContent = totalPackages;




// Calculate the total contributions across all countries
var totalContributions = 0;
for (var country in averageContributionsByCountry) {
    totalContributions += averageContributionsByCountry[country];
}

// Generate the average contribution by country section
var averageContributionsContainer = document.getElementById('average-contributions');
var html = '<h5 class="card-title">Average Contribution per package</h5>';

for (var country in averageContributionsByCountry) {
    var contributionPercentage = (averageContributionsByCountry[country] / totalContributions) * 100;
    html += '<div class="mb-3">';
    html += '<div class="d-flex align-items-center justify-content-between">';
    html += '<span>' + country + '</span>';
    html += '<span>' + contributionPercentage.toFixed(2) + '%</span>';
    html += '</div>';
    html += '<div class="progress">';
    html += '<div class="progress-bar" role="progressbar" style="width: ' + contributionPercentage + '%" aria-valuenow="' + contributionPercentage + '" aria-valuemin="0" aria-valuemax="100"></div>';
    html += '</div>';
    html += '</div>';
}

document.getElementById("average-contributions").innerHTML = html;




// Generate the best package per region section
var bestPackageContainer = document.getElementById('best-package');
var html = '<h5 class="card-title">Best Package per Region</h5>';

for (var region in bestPackagesByRegion) {
    html += '<div class="mb-3">';
    html += '<h6>' + region + '</h6>';

    var largestPackageSize = 0;
    var largestPackageCountry = "";

    for (var country in bestPackagesByRegion[region]) {
        var packageSize = bestPackagesByRegion[region][country].size;

        if (packageSize > largestPackageSize) {
            largestPackageSize = packageSize;
            largestPackageCountry = country;
        }
    }

    html += '<div class="card">';
    html += '<div class="card-body">';
    html += '<h6 class="card-title">' + largestPackageCountry + '</h6>';
    html += '<p class="card-text">Package: ' + bestPackagesByRegion[region][largestPackageCountry].package + '</p>';
    html += '<p class="card-text">Total commits: ' + largestPackageSize + '</p>';
    html += '</div>';
    html += '</div>';

    html += '</div>';
}

document.getElementById('best-package').innerHTML = html;

// Color for each world region
mapRegionToColor = {
    "North America" : "#2C77B8 ",
    "Central and South America" : "#FFA500 ",
    "Africa" : "#5CB85C ",
    "Europe" : "#FF4C4C ",
    "Russia" : "#993399 ",
    "West Asia" : "#d9b702 ",
    "Central and South Asia" : "#5E2CA5 ",
    "China" : "#FF69B4 ",
    "East Asia" : "#7fbd20 ",
    "Southeast Asia" : "#02b2b5 ",
    "Pacific" : "#00FF7F ",
    "Australia and New Zealand" : "#FF8C00 ",

}

//  Create the map
var svg = d3.select("svg"),
    width = +svg.attr("width"),
    height = +svg.attr("height");


// Map and projection
var projection = d3.geoNaturalEarth1()
    .scale(width / 1.5 / Math.PI)
    .translate([width / 2.2, height / 1.75])

const map = new Map();


// Load external data and boot
d3.json("https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson", 
function(data){
    // console.log(data)
    
    // Draw the map
    svg
        .append("g")
        .selectAll("path")
        .data(data.features)
        .enter()
        .append("path")
        .attr("id", function(d){
            index = countryMatchFrontBack[0].countryFront.indexOf(d.properties.name);
            country = countryMatchFrontBack[0].countryBack[index];
            return country})
        .attr("d", d3.geoPath()
            .projection(projection)
        )
        .attr("class", "country");

    
    // Adding labels to the circles
    svg
        .append("g")
        .selectAll("text")
        .data(circleData)
        .enter()
        .append("text")
        .text(d => d.name)
        .attr("x", function(d){
            return projection([d.homelong - 10, d.homelat])[0]})
        .attr("y", function(d){
            return projection([d.homelong, d.homelat - 5])[1]})
        .attr("color", "black")
        .attr("font-size", 10)
        .attr("font-type", "Sans Serif")
        .attr("font-weight", 700)

    // Adding Legend
    var valuesToShow = [10, 50]
    var xCircle = 80
    var xLabel = 90
    svg
        .selectAll("legend")
        .data(valuesToShow)
        .enter()
        .append("circle")
        .attr("cx", xCircle)
        .attr("cy", function(d){ return height - d*1.5 } )
        .attr("r", function(d){ return d*1.5 })
        .style("fill", "none")
        .attr("stroke", "black")

    // Add legend: segments
    svg
        .selectAll("legend")
        .data(valuesToShow)
        .enter()
        .append("line")
        .attr('x1', function(d){ return xCircle + d*1.5 } )
        .attr('x2', xLabel + 90)
        .attr('y1', function(d){ return height - d*1.5 } )
        .attr('y2', function(d){ return height - d*1.5 } )
        .attr('stroke', 'black')
        .style('stroke-dasharray', ('2,2'))

    // Add legend: labels
    svg
        .selectAll("legend")
        .data(valuesToShow)
        .enter()
        .append("text")
        .attr('x', xLabel + 90)
        .attr('y', function(d){ return height - d*1.5 } )
        .text( function(d){ return d } )
        .style("font-size", 15)
        .attr("font-type", "Sans Serif")
        .attr("font-weight", 500)
        .attr('alignment-baseline', 'middle')

    // Add title
    svg
        .append("text")
        .attr("text-anchor", "end")
        .style("fill", "black")
        .attr("x", 90)
        .attr("y", height - 160)
        .attr("width", 90)
        .html("Legend : ")
        .attr("font-type", "Sans Serif")
        .style("font-size", 15)
        .attr("font-weight", 700)

})


// Data for the circles, the places on the map and the corresponding region
var circleData = [
    {homelong : -100, homelat : 45, n : 0, color : "#235E95", name : "North America"}, // North America
    {homelong : -75, homelat : 5, n : 0, color : "#FFA500 ", name : "Central and South America"}, // Central and south America
    {homelong : 25, homelat : 15, n : 0, color : "#5CB85C ", name : "Africa"}, // Africa
    {homelong : 10, homelat : 50, n : 0, color : "#FF4C4C ", name : "Europe"}, // Europe
    {homelong : 80, homelat : 63, n : 0, color : "#993399 ", name : "Russia"}, // Russia
    {homelong : 45, homelat : 35, n : 0, color : "#d9b702 ", name : "West Asia"}, // West Asia
    {homelong : 75, homelat : 20, n : 0, color : "#5E2CA5 ", name : "Central and South Asia"}, // Central and south Asia
    {homelong : 107, homelat : 37, n : 0, color : "#FF69B4 ", name : "China"}, // China
    {homelong : 135, homelat : 40, n : 0, color : "#7fbd20 ", name : "East Asia"}, // East Asia
    {homelong : 110, homelat : 10, n : 0, color : "#02b2b5 ", name : "Southeast Asia"},// Southeast Asia
    {homelong : 160, homelat : 15, n : 0, color : "#00FF7F ", name : "Pacific"}, // Pacific
    {homelong : 130, homelat : -25, n : 0, color : "#FF8C00 ", name : "Australia and New Zealand"}, // Australia and new Zealand
    // {homelong : 0, homelat : -50, n : 0, color : "grey ", name : "Unknown"}, // Unknown

]


// This function is used for the load button
function loading(){
    console.log("loading");
    button = document.getElementById("generate_button");
    button.innerHTML = "  <i class='fa fa-spinner fa-spin'></i>Loading";
    button.disabled = true;
}


// This function is used to stop the load button
function stopLoading(){
    console.log("stop loading");
    button = document.getElementById("generate_button");
    button.innerHTML = "  Search";
    button.disabled = false;
}


// Gets the data from the backend and places it on the map and the table
function generate(){

    // Add the loading animation
    loading();
    
    // reset each world region circle
    circleData.forEach(element => {
        element.n = 0;
    });

    // reset the color of each country
    resetCountry = document.getElementsByClassName("notCountry");
    while (resetCountry.length > 0){
        resetCountry[0].setAttribute("class", "country");
    }

    // get the package name entered by the user and return an error if not package name found
    packageName = document.getElementById("package_name").value;
    if (packageName == ""){
		alert("Please enter a package name");
        stopLoading();
		return 0;
	}

    // We enable multiprocessing in JS to have a loading animation during the loading of the data
    const requestPromise = new Promise((resolve, reject) => {

        const xhr = new XMLHttpRequest();
        
        xhr.onreadystatechange = function() {
          if (xhr.readyState === 4) {
            if (xhr.status === 200) {
            //   // Resolve the Promise with the response
              resolve(JSON.parse(xhr.responseText));
            
            // resolve(xhr.responseText);
            } else {
              // Reject the Promise with the error message
              reject('Request failed');
            }
          }
        };
        
        // Open and send the XHR request
        url = "scriptAndDatabase/getData.php?package_name=" + packageName;
        xhr.open('GET', url, true);
        xhr.send();
    });


    requestPromise
    .then(response => {
        console.log(response);

        data = response;
        if (data == "No data for this repository"){
            alert("No data for this repository, please verify the package name");
            stopLoading();
            data = {"region" : [], "contributions" : []}
        }

        // We remove all the data present in the matrix next to the map
        matrixData = document.getElementById("tableBody");
        matrixData.innerHTML = "";

        names = data.region;
        values = data.contributions;

        // console.log(names);
        // console.log(values);

        // we get the total contributions of the package
        total = 0;
        values.forEach((element)=>{
            total += parseInt(element);
        });

        //  Getting values in percentage of contribution
        percentage = [];
        values.forEach((value)=> {
            temp = parseInt(value)/total*100;
            
            percentage.push(temp);
        })

        // We set the circle width in proprotion of the country contributions 
        for (var i = 0; i < circleData.length; i++){
            checkIn = 0;
            for (var j = 0; j < names.length; j++){
                index = matchCountryRegion[0].country.indexOf(names[j]);
                region = matchCountryRegion[0].regions[index];

                // We sum all the contirbutions for this world region
                if (circleData[i].name == region){
                    checkIn = 1;
                    circleData[i].n += Math.round(percentage[j]*100)/100;
                }
            }
            // If we find no country from this world region we set this world region circle to 0
            if (checkIn == 0){
                circleData[i].n = 0;
            }
        }

        // We create the table with the row number, the name of the country and the contribution
        names.forEach((element, index) => {
            bigCell = document.createElement("tr");
            cell1 = document.createElement("th");
            cell1.scope = "row";
            
            cell1Text = document.createTextNode(index + 1);

            countryCell = document.createElement("td");
            contributionCell = document.createElement("td");
            
            countryValue = document.createTextNode(names[index]);
            ContributionValue = document.createTextNode((percentage[index]).toFixed(2) + "%");

            cell1.appendChild(cell1Text);
            countryCell.appendChild(countryValue);
            contributionCell.appendChild(ContributionValue);

            bigCell.appendChild(cell1);
            bigCell.appendChild(countryCell);
            bigCell.appendChild(contributionCell);

            matrixData.appendChild(bigCell);
        });

        // Adding circles to the map to represent each region contribution
        d3.queue()
        .defer(d3.json, "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson")  // World shape
        .defer(d3.csv, "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/data_gpsLocSurfer.csv") // Position of circles
        .await(ready);

        function ready(error, dataGeo, data) {
                
            //  Elements to enable mouve hover
            var Tooltip = d3.select("#mapDiv")
            .append("div")
            .attr("class", "tooltip")
            .style("opacity", 0)
            .style("background-color", "white")
            .style("border", "solid")
            .style("border-width", "2px")
            .style("border-radius", "5px")
            .style("padding", "5px")

            // Three function that change the tooltip when user hover / move / leave a cell
            var mouseover = function(d) {
                Tooltip.style("opacity", 1)
            }

            var mousemove = function(d) {
                Tooltip
                    .html(d.name + "<br>" + "contribution: " + d.n.toFixed(2) + "%")
                    .style("left", (d3.mouse(this)[0] + window.screen.width/2 - 800) + "px")
                    .style("top", (d3.mouse(this)[1] + 200) + "px")
            }

            var mouseleave = function(d) {
                Tooltip
                    .style("opacity", 0)        
                    .style("left", 0 + "px")
                    .style("top", 0 + "px")
            }

            // We remove all the world circle on the map
            if ((temp = document.getElementById("Circles"))){
                temp.remove();
            }

            // Drawing the circles
            svg
                .append("g")
                .attr("id", "Circles")
                .selectAll("myCircles")
                .data(circleData)
                .enter()
                .append("circle")
                .attr("cx", function(d){
                    return projection([d.homelong, d.homelat])[0]})
                .attr("cy", function(d){
                    return projection([d.homelong, d.homelat])[1]})
                .attr("r", function(d){
                    if (d.n < 1 && d.n > 0){
                        return 1
                    }
                    else {
                        return d.n*1.5
                    }})
                .style("fill", function(d){return d.color})
                .attr("stroke", "black")
                .attr("stroke-width", 2)
                .attr("fill-opacity", 0.5)
                .on("mouseover", mouseover)
                .on("mousemove", mousemove)
                .on("mouseleave", mouseleave)
        }

        // We change the color of the country of this package occordingly to the world region they are from
        data.region.forEach(element => {
            country = document.getElementById(element);
            if (country != null){

                index = matchCountryRegion[0].country.indexOf(element);
                region = matchCountryRegion[0].regions[index];
        
                color = mapRegionToColor[region];
                country.setAttribute("class", "notCountry");
                country.setAttribute("fill", color);
                country.setAttribute("opacity", 0.8);
            }
            if (country == null && element != "Unknown"){
                console.log("couldnt display country : ", element);
            }
        });

        // We stop the loading animation after all that
        stopLoading();
    })

    // If we get an error from the php page we console log the error
    .catch(error => {
        console.log(error);
        stopLoading();
    });

}
