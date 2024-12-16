window.onload = function() {
    var modal = document.getElementById("myModal");
    var btn = document.getElementById("openModalBtn");
    var span = document.getElementById("coffeechat-modal-close");

    btn.onclick = function() {
        modal.style.display = "flex";
    }

    // 모달 닫기 (X 버튼 클릭 시)
    span.onclick = function() {
        modal.style.display = "none";
    }

    // 모달 닫기 (모달 외부 클릭 시)
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
};

document.addEventListener("DOMContentLoaded", function() {
    // 모달 관련 변수 정의
    const modal = document.getElementById("coffeechatModal");
    const modalContent = document.getElementById("coffeechatModalContent");
    const modalbutton = document.getElementById("coffeechatModalContentBtn")
    const closeModalBtn = document.getElementById("coffeechatModalClose");

    // "커피챗 문구보기" 버튼 클릭 시 모달 열기
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('btn-accept-letter')) {
            const letterContent = event.target.getAttribute('data-letter');
            const urlRej = event.target.getAttribute('data-url-rej');
            const urlAcc = event.target.getAttribute('data-url-acc');
            console.log('accept')
            console.log(letterContent)


            modalContent.innerHTML = `
                <p class="letter-area">${letterContent.replace(/\r?\n/g, '<br>')}</p>
            `;
            modalbutton.innerHTML = `
                <button type="button" class="btn-accept modal-accept" data-url="${urlAcc}">Accept</button>
            `;
            modal.style.display = "flex";
        }

        if (event.target.classList.contains('btn-view-letter')) {
            const letterContent = event.target.getAttribute('data-letter');

            modalContent.innerHTML = `
                <p class="letter-area">${letterContent.replace(/\r?\n/g, '<br>')}</p>
            `;
            modalbutton.innerHTML = `
                
            `;
            modal.style.display = "flex";
        }
        if (event.target.classList.contains('btn-accept modal-accept')) {
            modal.style.display = "none";

        }
    });

    // 모달 닫기 (X 버튼 클릭 시)
    closeModalBtn.onclick = function() {
        modal.style.display = "none";
    }

    // 모달 닫기 (모달 외부 클릭 시)
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
});

$(document).ready(function() {
    function toggleModalCSS(load) {
        const modalCSSId = 'modal-css';
        if (load) {
            if ($('#' + modalCSSId).length === 0) {
                var link = document.createElement('link');
                link.rel = 'stylesheet';
                link.href = '{% static "css/mypage/profile_modal.css" %}';
                link.id = modalCSSId;
                document.head.appendChild(link);
            }
        } else {
            var link = document.getElementById(modalCSSId);
            if (link) {
                document.head.removeChild(link);
            }
        }
    }

    $(document).on('click', '.coffeechat-card', function (event) {
        event.preventDefault();
        var userId = event.target.getAttribute('data-coffeechat-sender-id')
        var url = `/mypage/ajax/profile-modal`;


        // Make an AJAX request to load the modal content
        $.ajax({
            url: url,
            data: {'user_id': userId},
            success: function (response) {
                $('#modal-profile-content').html(response);
                $('#profile_modal').show();

                // 모달 로드 후 스크립트 초기화
                initializeProfileModal(userId);

            },
            error: function (xhr) {
                alert('프로필을 불러오는 중 오류가 발생했습니다.');
            }
        });
    });

    $('.close-button').click(function () {
        $('#profile_modal').hide();
        toggleModalCSS(false);  // CSS 파일 제거
    });

    $(window).click(function (event) {
        if (event.target.id === 'profile_modal') {
            $('#profile_modal').hide();
            toggleModalCSS(false);  // CSS 파일 제거
        }
    });
});