msgtools = (($, w)->

    showAlert = (content, duration=2000) ->
        $("#page-alert [name=content]").html content
        $('#page-alert').removeClass 'hide'
        setTimeout removeAlert, duration
    removeAlert = ->
        $("#page-alert").addClass 'hide'

    showMsg = (id, duration) ->
        removeMsg()
        $('#page-posting-bg').removeClass('hide')
        $('#page-posting').removeClass('hide')
        $("##{id}").removeClass('hide')
        setTimeout removeMsg, duration if duration

    removeMsg = ->
        $('#page-posting').addClass('hide')
        $('#page-posting-bg').addClass('hide')
        $('#page-posting-view').addClass('hide')
        $('#page-posting-error').addClass('hide')
        $('#page-posting-success').addClass('hide')

    showConfirm = (content, cancel, confirm, cancel_text='取消', confirm_text='确定') ->
        $('#page-confirm [name="content"]').html content
        $('#page-confirm [name="confirm-text"]').html confirm_text
        $('#page-confirm [name="cancel-text"]').html cancel_text
        $('#page-confirm').removeClass 'hide'
        $('#page-backdrop').removeClass 'hide'
        $('#page-confirm [name="confirm"]').on 'click', (->
            removeConfirm()
            confirm?()
        )
        $('#page-confirm [name="cancel"]').on 'click', (->
            removeConfirm()
            cancel?()
        )

    removeConfirm = ->
        $('#page-confirm').addClass 'hide'
        $('#page-backdrop').addClass 'hide'


    makeBodyGray: -> $('body').css 'background-color', '#e8edf1'
    showMsg: showMsg
    showAlert: showAlert
    removeAlert: removeAlert
    showConfirm: showConfirm
)(Zepto, window)

module.exports = msgtools
