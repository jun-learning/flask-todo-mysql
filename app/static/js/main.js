// カスタムJavaScript

// フラッシュメッセージ自動非表示
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');

    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);  // 5秒後に自動でメッセージを閉じる
    });
});

// フォームバリデーション
(function() {
    'use strict';

    const forms = document.querySelectorAll('.needs-validation');

    Array.from(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }

            form.classList.add('was-validated');
        }, false);
    });
})();

// カスタムJavaScript

// フラッシュメッセージ自動非表示
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');

    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();  // 5秒後に Bootstrap のアラートを閉じる
        }, 5000);
    });

    // チェックボックスアニメーション
    const checkboxes = document.querySelectorAll('.form-check-input[type="checkbox"]');
    checkboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            const label = this.nextElementSibling;
            if (this.checked) {
                label.style.transition = 'all 0.3s ease';
                label.style.opacity = '0.6';  // チェック時に薄く表示
            }
        });
    });
});

// フォームバリデーション
(function() {
    'use strict';

    const forms = document.querySelectorAll('.needs-validation');

    Array.from(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }

            form.classList.add('was-validated');
        }, false);
    });
})();