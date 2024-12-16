function initializeProfileModal(userId) {
    document.getElementById('close-button').addEventListener('click', function() {
        document.getElementById('profile_modal').style.display = 'none';
    });

    loadActivities('my_posts', 'all', userId);

    const activityLinks = document.querySelectorAll('.activity-link');
    const filterLinks = document.querySelectorAll('.filter-link');

    activityLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const currentFilter = this.getAttribute('data-filter');
            activityLinks.forEach(link => link.classList.remove('active'));
            this.classList.add('active');
            loadActivities(currentFilter, 'all', userId);
        });
    });

    filterLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const currentCategory = this.getAttribute('data-category');
            filterLinks.forEach(link => link.classList.remove('active'));
            this.classList.add('active');
            loadActivities('my_posts', currentCategory, userId);
        });
    });

    function loadActivities(filter, category, userId) {
        const url = `/mypage/ajax/activities/?filter=${filter}&category=${category}&user_id=${userId}`;

        //이미지 로딩 부분 제외
        // const profileModal = document.getElementById('profile_modal');
        // const randomImageUrl = profileModal.getAttribute('data-random-image-url');
        // console.log(randomImageUrl)

        //<div class="card-image" style="background-image: url('${randomImageUrl}');"></div> 

        fetch(url)
            .then(response => response.json())
            .then(data => {
                const activityContent = document.getElementById('activity-content');
                activityContent.innerHTML = '';

                if (data.posts && data.posts.length > 0) {
                    data.posts.forEach(post => {
                        const postElement = document.createElement('div');
                        postElement.classList.add('activity-card');

                        postElement.innerHTML = `
                            <a href="${post.url}" class="card-link">
                                <div class="card-content">
                                    <h3>${post.title}</h3>
                                    <br/>
                                    <span>작성자: ${post.writer}</span><br/>
                                    <span>날짜: ${new Date(post.date).toLocaleDateString()}</span>
                                </div>
                            </a>
                        `;
                        activityContent.appendChild(postElement);
                    });
                } else {
                    activityContent.innerHTML = '<p>해당하는 글이 없습니다.</p>';
                }
            })
            .catch(error => console.error('Error loading activities:', error));
    }
}
