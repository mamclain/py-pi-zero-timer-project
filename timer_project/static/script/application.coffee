# Yep... Most Folks are going to hate my selection of CoffeeScript... yes, its old and antiquated...
# yes I should use something more modern...  but as someone who does python development on the regular the
# convenience of not having to swap code paradigms is my rational...

class window.Application
  constructor: () ->

    @ko_hours = ko.observable("")
    @ko_minutes = ko.observable("")
    @ko_seconds = ko.observable("")
    @ajax_start_event = ko.observable(false)
    @ajax_run_event = ko.observable(false)
    @ajax_started = ko.observable(false)
    @status_hours = ko.observable("")
    @status_minutes = ko.observable("")
    @status_seconds = ko.observable("")
    @ajax_stop_event = ko.observable(false)

    @error_body = ko.observable("Error Body")
    @error_title = ko.observable("Error Title")

    @show_error = (title,error) =>
      @error_body(error)
      @error_title(title)
      $('#errorModal').modal('show')

    @cast_number = (value)=>
      if value == ""
        return 0
      value = parseFloat(value)
      if value == NaN
        return 0
      return value

    @start_event = =>
      @status_hours(@cast_number(@ko_hours()))
      @status_minutes(@cast_number(@ko_minutes()))
      @status_seconds(@cast_number(@ko_seconds()))
      @ajax_start_event(true)
      $.post 'ajax/',
        request: "ajax_start_event"
        hours: @ko_hours()
        minutes:@ko_minutes()
        seconds:@ko_seconds()
        (data) =>
          @ajax_start_event(false)
          result = JSON.parse(data)
          if(result.Error)
            @show_error("Timer Start Error", result.Message)
          else
            @ajax_run_event(true)

    @stop_event = =>
      @ajax_stop_event(true)
      $.post 'ajax/',
        request: "ajax_stop_event"
        (data) =>
          @ajax_stop_event(false)
          result = JSON.parse(data)
          if(result.Error)
            @show_error("Timer Stop Error", result.Message)
          else
            @ajax_run_event(false)

    @ajax_stastus = =>
      $.post 'ajax/',
        request: "ajax_get_status"
        (data) =>
          @ajax_started(true)
          result = JSON.parse(data)
          if(result.Error)
            @show_error("Major Timer Error", result.Message)
          else
            if(result.Status)
              base_time = result.Left

              base_hour = Math.floor(base_time/(60.0*60.0))
              base_time -= base_hour*60.0*60.0
              base_min = Math.floor(base_time/(60.0))
              base_time -= base_min*60.0
              base_second = Math.floor(base_time)
              @status_hours(base_hour)
              @status_minutes(base_min)
              @status_seconds(base_second)
              @ajax_run_event(true)
            else
              @ajax_run_event(false)

    @start_app = =>
      @ajax_stastus()
      window.setInterval(@ajax_stastus, 500);


# ******************************************************************************
# Setup Knockout.js ViewModel
# ******************************************************************************
window.app = new window.Application()
$ ->
  window.app.start_app()
  ko.applyBindings(window.app)


