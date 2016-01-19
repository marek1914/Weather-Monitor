$(document).ready(function() {

// ref - http://www.jqueryscript.net/animation/Javascript-Animated-Gauges-Plugin-JustGage.html

  var tempGauge;

  window.onload = function(){

    var tempGauge = new JustGage({
      id: "temp-gauge",
      //value: getRandomInt(61,99),
      value: 0,
      min: -10,
      max: 110,
      decimals: 1,
      title: "",
      label: "Temp \xB0" + units_temp,
      labelMinFontSize: 14,
      levelColors: ["#E8A9E6", "#22B5E6", "#53E622", "#E65322"],
      pointer: true,
      gaugeWidthScale: 1.0,
      noGradient: true,
    });

    if (metric) {
      tempGauge.min = -50;
      tempGauge.max = 50;
    }

    // create the canvas for the wind compass
    $('#wind-compass').html('<canvas width=130, height=130></canvas>');

    function drawWindCompass(curr, min, max) {
      // for jcanvas docs, see - http://projects.calebevans.me/jcanvas/docs/arcs/
      var radius = 50;
      var xpos = 65, ypos = 65;
      var strokeW = 5;

      $('#wind-compass canvas')
      .clearCanvas()
      // draw the recent wind history
      .drawSlice({
        fillStyle: '#A7DFF2',
        x: xpos, y: ypos,
        radius: radius,
        // start and end angles in degrees
        start: min, end: max,
      })

      // draw the background circle
      .drawArc({
        strokeStyle: 'tan',
        strokeWidth: strokeW,
        x: xpos, y: ypos,
        radius: radius,
      })
      // draw the compass points
      .drawLine({
        strokeStyle: '#000',
        strokeWidth: 1,
        x1: xpos-radius, y1: ypos,
        x2: xpos-radius+10, y2: ypos,
      })
      .drawLine({
        strokeStyle: '#000',
        strokeWidth: 1,
        x1: xpos+radius, y1: ypos,
        x2: xpos+radius-10, y2: ypos,
      })
      .drawLine({
        strokeStyle: '#000',
        strokeWidth: 1,
        x1: xpos, y1: ypos-radius,
        x2: xpos, y2: ypos-radius+10,
      })
      .drawLine({
        strokeStyle: '#000',
        strokeWidth: 1,
        x1: xpos, y1: ypos+radius,
        x2: xpos, y2: ypos+radius-10,
      })

      .drawText({
        fillStyle: '#9cf',
        strokeStyle: '#25a',
        strokeWidth: 1,
        x: xpos-radius-10, y: ypos,
        fontSize: 10,
        fontFamily: 'Verdana, sans-serif',
        text: 'W'
      })
      .drawText({
        fillStyle: '#9cf',
        strokeStyle: '#25a',
        strokeWidth: 1,
        x: xpos+radius+10, y: ypos,
        fontSize: 10,
        fontFamily: 'Verdana, sans-serif',
        text: 'E'
      })
      .drawText({
        fillStyle: '#9cf',
        strokeStyle: '#25a',
        strokeWidth: 1,
        x: xpos, y: ypos-radius-10,
        fontSize: 10,
        fontFamily: 'Verdana, sans-serif',
        text: 'N'
      })
      .drawText({
        fillStyle: '#9cf',
        strokeStyle: '#25a',
        strokeWidth: 1,
        x: xpos, y: ypos+radius+10,
        fontSize: 10,
        fontFamily: 'Verdana, sans-serif',
        text: 'S'
      })

      // draw the pointer
      .rotateCanvas({
        rotate: curr,
        x: xpos, y: ypos
      })
      .translateCanvas({
        translateX: 0, translateY: -radius
      })
      .drawPath({
              strokeStyle: '#000',
              strokeWidth: 1,
              fillStyle: 'red',
              closed: true,
              p1: {
                type: 'line',
                x1: xpos-2, y1: ypos-2,
                x2: xpos, y2: ypos+25,
                x3: xpos+2, y3: ypos-2,
              },
      })
      .restoreCanvas()
      .restoreCanvas() // we must do it twice - once for each transform op
    ;
    }


    setInterval(function() {
      //tempGauge.refresh(getRandomInt(61,99));
      $("#update-time").load("/lastupdate/",function() {
      });
      $.getJSON("/temperature/", function( data ) {
        tempGauge.refresh(data["temperature"]);
        $("#other-temp .humidity").html(data["humidity"]);
        $("#other-temp .heatindex").html(data["heatindex"]);
        $("#other-temp .windchill").html(data["windchill"]);
        $("#other-temp .feel").html(data["feel"]);
        $("#other-temp .dewpoint").html(data["dewpoint"]);
      });
      $.getJSON("/hilo_temps/", function( data ) {
        $("#temp-forecast .label.past1").html(data["past1_label"]+':');
        $("#temp-forecast .value.past1").html(data["past1_value"]);
        $("#temp-forecast .label.past2").html(data["past2_label"]+':');
        $("#temp-forecast .value.past2").html(data["past2_value"]);

        $("#temp-forecast .label.future1").html(data["future1_label"]+':');
        $("#temp-forecast .value.future1").html(data["future1_value"]);
        $("#temp-forecast .label.future2").html(data["future2_label"]+':');
        $("#temp-forecast .value.future2").html(data["future2_value"]);
      });

      $.getJSON("/outlook/", function( data ) {
        $("#outlook-text").html(data["outlook"]);
        $("#outlook-icon").attr("src", data["icon"]);
        $("#pressure").html(data["pressure"]);
        $("#presstrend").html(data["presstrend"]);
      });
      $.getJSON("/wind/", function( data ) {
        //data['currdir']
        //var currdir = getRandomInt(0,120);
        drawWindCompass(data['currdir'], data['mindir'], data['maxdir']);
        $("#wind-speed").html(data["speed"]);
        $("#wind-gusts").html(data["gusts"]);
      });
    }, 5000);
  };

}); // doc.ready
/*
      temperature=cond.getTemperature(),
      humidity = cond.humidity,
      heatindex = cond.getHeatIndex(),
      windchill = cond.getWindChill(),
      feel = cond.getRealFeel(),
      dewpoint = cond.getDewpoint()
*/