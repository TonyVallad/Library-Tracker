document.addEventListener('DOMContentLoaded', () => {
	setTimeout(() => {
		document.querySelectorAll('[data-flash]').forEach((el) => {
			el.remove();
		});
	}, 3000);
});
