frappe.pages['talent_management'].on_page_load = function (wrapper) {
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('Talent Management'),
        single_column: true
    });

    $(frappe.render_template('talent_management', {})).appendTo(page.main);

    // Primary Left Bar Modules based on your Workspace App launcher
    const modules = [
        { id: 'expenses', label: 'Expenses', icon: 'octicon-credit-card', route: 'expenses' },
        { id: 'hr_setup', label: 'HR Setup', icon: 'octicon-gear', route: 'hr-setup' },
        { id: 'hrpro', label: 'HRPRO', icon: 'octicon-organization', route: 'dashboard-view/HRPRO' },
        { id: 'leaves', label: 'Leaves', icon: 'octicon-calendar', route: 'leaves' },
        { id: 'payroll', label: 'Payroll', icon: 'octicon-briefcase', route: 'payroll' },
        { id: 'performance', label: 'Performance', icon: 'octicon-meter', route: 'performance' },
        { id: 'recruitment', label: 'Recruitment', icon: 'octicon-person-add', route: 'recruitment' },
        { id: 'shift_attendance', label: 'Shift & Attendance', icon: 'octicon-clock', route: 'shift-%26-attendance' },
        { id: 'tax_benefits', label: 'Tax & Benefits', icon: 'octicon-tag', route: 'tax-%26-benefits' },
        { id: 'tenure', label: 'Tenure', icon: 'octicon-milestone', route: 'tenure' }
    ];

    const $primaryNav = $('#talent-primary-items');
    const $target = $('#talent-viewport-container');

    // Clean duplicate Desk header/navbar inside iframe
    function cleanIframeContent(iframe) {
        try {
            const frameDoc = iframe.contentDocument || iframe.contentWindow.document;
            if (!frameDoc) return;

            const styleId = 'frappe-clean-desk-style';
            if (!frameDoc.getElementById(styleId)) {
                const style = frameDoc.createElement('style');
                style.id = styleId;
                style.innerHTML = `
                    /* Remove redundant top header navigation bar */
                    .navbar,
                    header.navbar {
                        display: none !important;
                    }

                    /* Adjust workspace padding to fit edge-to-edge */
                    .page-container {
                        margin-top: 0 !important;
                        padding-top: 0 !important;
                    }
                `;
                frameDoc.head.appendChild(style);
            }
        } catch (e) {
            // Suppress cross-origin frame exceptions
        }
    }

    // Load selected workspace directly inside iframe
    function loadWorkspace(module) {
        $target.empty();

        const targetUrl = `/desk/${module.route}`;

        const $iframe = $('<iframe>', {
            src: targetUrl,
            class: 'tm-viewport-iframe',
            frameborder: '0',
            style: 'width: 100%; height: 100%; border: none;'
        });

        $iframe.on('load', function () {
            cleanIframeContent(this);
            setTimeout(() => cleanIframeContent(this), 300);
            setTimeout(() => cleanIframeContent(this), 800);
        });

        $target.html($iframe);
    }

    // Generate Left Sidebar Buttons
    modules.forEach((mod, idx) => {
        const $btn = $(`
            <li class="tm-primary-item ${idx === 0 ? 'active' : ''}" data-id="${mod.id}">
                <div class="primary-icon">${frappe.utils.icon(mod.icon, 'md')}</div>
                <span class="primary-label" >${__(mod.label)}</span>
            </li>
        `);

        $btn.on('click', function () {
            $('.tm-primary-item').removeClass('active');
            $(this).addClass('active');
            loadWorkspace(mod);
        });

        $primaryNav.append($btn);
    });

    // Automatically load the first module on initial view
    loadWorkspace(modules[0]);
};