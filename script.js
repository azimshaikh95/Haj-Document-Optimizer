// 1. Strip the copy/paste/cut restrictions from ALL text fields
var sensitiveFields = [
    'passport_no', 'issue_place', 'issue_date', 'expiry_date', 'birth_date', 'applicant_first_name', 'applicant_last_name', 'birth_place', 
    'c_passport_no', 'c_issue_place', 'c_issue_date', 'c_expiry_date', 'c_birth_date', 'c_applicant_first_name', 'c_applicant_last_name', 'c_birth_place',
    'account_holder_name', 'bank_name', 'account_number', 'ifsc_code',
    'c_account_holder_name', 'c_bank_name', 'c_account_number', 'c_ifsc_code'
];

sensitiveFields.forEach(function(id) {
    var $el = $('#' + id);
    if ($el.length) {
        $el.off('copy paste cut drop keydown.prevent-shortcuts contextmenu.prevent-shortcuts');
    }
});

// 2. Unlock date fields safely and wire them to the site's calculation rules
var dateFields = ['#issue_date', '#expiry_date', '#birth_date', '#c_issue_date', '#c_expiry_date', '#c_birth_date'];

dateFields.forEach(function(selector) {
    var $el = $(selector);
    if ($el.length) {
        // Unlock field for editing/pasting
        $el.removeAttr('readonly').prop('readonly', false).css('background-color', '#fff');
        
        // Remove the restrictive paste blockers
        $el.off('paste drop contextmenu');

        // When you paste or change a date, update the system validation natively
        $el.on('blur input change keyup paste', function() {
            var fieldId = $(this).attr('id');
            var val = $(this).val();

            // Natively calculate age if it's the main or confirmation birth date field
            if ((fieldId === 'birth_date' || fieldId === 'c_birth_date') && val.includes('-')) {
                try {
                    var calculatedAge = calculateAge(val);
                    if (fieldId === 'birth_date') {
                        $('#age').val(calculatedAge);
                        $('#frmedit').bootstrapValidator('revalidateField', 'age');
                    } else {
                        $('#c_age').val(calculatedAge);
                        $('#frmedit').bootstrapValidator('revalidateField', 'c_age');
                    }
                } catch(e) {
                    console.log("Age engine bypass update active.");
                }
            }

            // Revalidate the current date field with the page engine
            try {
                $('#frmedit').bootstrapValidator('revalidateField', $(this).attr('name'));
            } catch(e) {}
        });
    }
});

console.log("✅ Safe Patch Applied. Paste dates freely; the system will safely auto-calculate age.");
