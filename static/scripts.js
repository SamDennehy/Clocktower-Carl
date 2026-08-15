const generateButton = document.getElementById('generate-script');
const downloadButton = document.getElementById('download-script');
const scriptContainer = document.getElementById('script-container');
const drunktowerButton = document.getElementById('get-drinktower-bootleggers');
let generatedScript = null;

generateButton.addEventListener('click', async () => {
	const payload = {
		townsfolk: Number(document.getElementById('townsfolk').value),
		outsiders: Number(document.getElementById('outsiders').value),
		minions: Number(document.getElementById('minions').value),
		demons: Number(document.getElementById('demons').value),
		npcs: Number(document.getElementById('npcs').value),
	};

	const response = await fetch('/generate_script_preview', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify(payload),
	});

	const data = await response.json();
	generatedScript = data;
    drawScriptPreview(data);

	const storytellerCount = generatedScript.some((role) => role.id === 'knaves') ? 2 : 1;
	const storytellersInput = document.getElementById('storytellers');
	const storytellers = storytellersInput.value
		.split(',')
		.map((name) => name.trim())
		.filter((name) => name.length > 0);
	const pickedStorytellers = pickRandomStorytellers(storytellers, storytellerCount);
	const storytellerContainer = document.getElementById('storyteller-container');

	if (pickedStorytellers.length === 0) {
		storytellerContainer.textContent = 'Storyteller: (none provided)';
		return;
	}

	storytellerContainer.textContent = `Storyteller${pickedStorytellers.length > 1 ? 's' : ''}: ${pickedStorytellers.join(', ')}`;
}); 

function pickRandomStorytellers(storytellers, count) {
	const pool = [...storytellers];
	const picks = [];
	const maxPicks = Math.min(count, pool.length);

	for (let index = 0; index < maxPicks; index += 1) {
		const randomIndex = Math.floor(Math.random() * pool.length);
		picks.push(pool[randomIndex]);
		pool.splice(randomIndex, 1);
	}

	return picks;
}

downloadButton.addEventListener('click', () => {
	if (!generatedScript) {
		return;
	}

	const downloadScript = [
		{
			id: 'placeholder',
			author: 'placeholder',
			name: 'placeholder',
		},
		...generatedScript
			.filter((role) => role && role.id !== '_meta')
			.map((role) => role.id),
	];

	const blob = new Blob([JSON.stringify(downloadScript, null, 2)], {
		type: 'application/json',
	});
	const url = window.URL.createObjectURL(blob);
	const link = document.createElement('a');
	link.href = url;
	link.download = 'script.json';
	link.click();
	window.URL.revokeObjectURL(url);
});

function drawScriptPreview(script) {
    const scriptContainer = document.getElementById('script-container');
    scriptContainer.innerHTML = '';

	const groups = [
		{ keys: ['townsfolk'], title: 'Townsfolk' },
		{ keys: ['outsider'], title: 'Outsiders' },
		{ keys: ['minion'], title: 'Minions' },
		{ keys: ['demon'], title: 'Demons' },
		{ keys: ['fabled', 'loric', 'npcs'], title: 'NPCs' },
	];

	const rolesByTeam = {};
	groups.forEach((group) => {
		group.keys.forEach((teamKey) => {
			rolesByTeam[teamKey] = [];
		});
	});

	script.forEach((role) => {
		if (!role || typeof role !== 'object' || role.id === '_meta') {
			return;
		}

		if (!rolesByTeam[role.team]) {
			rolesByTeam[role.team] = [];
		}

		rolesByTeam[role.team].push(role);
	});

	groups.forEach((group) => {
		const roles = group.keys.flatMap((teamKey) => rolesByTeam[teamKey] || []);
		if (!roles.length) {
			return;
		}

		const section = document.createElement('section');
		section.className = 'preview-group';

		const heading = document.createElement('h3');
		heading.className = 'preview-group-title';
		heading.textContent = group.title;

		const roleGrid = document.createElement('div');
		roleGrid.className = 'preview-role-grid';

		roles.forEach((role) => {
			const lineElement = document.createElement('div');
			lineElement.className = 'preview-role';

			const icon = document.createElement('img');
			const iconVariants = getRoleIconVariants(role);
			icon.src = iconVariants[0];
			icon.dataset.variantIndex = '0';
			icon.alt = `${role.name} icon`;
			icon.title = iconVariants.length > 1 ? 'Click to toggle icon variant' : role.name;

			const roleName = document.createElement('span');
			roleName.textContent = role.name;

			lineElement.appendChild(icon);
			lineElement.appendChild(roleName);
			roleGrid.appendChild(lineElement);
		});

		section.appendChild(heading);
		section.appendChild(roleGrid);
		scriptContainer.appendChild(section);
	});
}

function getRoleIconVariants(role) {
	const baseUrl = `https://release.botc.app/resources/characters/${role.edition}/${role.id}`;

	if (!role.alignment) {
		return [`${baseUrl}.webp`];
	}

	const primary = `${baseUrl}_${role.alignment}.webp`;
	const alternateAlignment = role.alignment === 'g' ? 'e' : 'g';
	const alternate = `${baseUrl}_${alternateAlignment}.webp`;

	return [primary, alternate];
}

drunktowerButton.addEventListener('click', async () => {
	const response = await fetch('/drunktower_bootleggers', {
		method: 'GET',
	});
	const bootleggers = await response.json();
	const container = document.getElementById('drunktower-bootleggers-container');
	container.innerHTML = '';

	//pick random from drunktower_bootleggers
	const randomIndex = Math.floor(Math.random() * bootleggers.length);
	const randomBootlegger = bootleggers[randomIndex];
	container.textContent = randomBootlegger;
});
