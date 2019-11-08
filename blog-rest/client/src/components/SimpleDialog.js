import React from 'react'
import PropTypes from 'prop-types'
import { withStyles } from '@material-ui/core/styles'
import Button from '@material-ui/core/Button'
import Dialog from '@material-ui/core/Dialog'
import DialogTitle from '@material-ui/core/DialogTitle'
import DialogActions from '@material-ui/core/DialogActions'
import DialogContent from '@material-ui/core/DialogContent'
import DialogContentText from '@material-ui/core/DialogContentText'

const styles = theme => ({
  root: {
  }
})

class SimpleDialog extends React.Component {
  render () {
    const { classes, onClose, open, dialogTitle, dialogContent } = this.props

    return (
      <Dialog className={classes.root} onClose={onClose} open={open}>
        <DialogTitle>
          {dialogTitle}
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            {dialogContent}
          </DialogContentText>
          <DialogActions>
            <Button onClick={onClose} color='primary'>
              Dismiss
            </Button>
          </DialogActions>
        </DialogContent>
      </Dialog>
    )
  }
}

SimpleDialog.apply.propTypes = {
  classes: PropTypes.object.isRequired,
  onClose: PropTypes.func.isRequired,
  open: PropTypes.bool.isRequired,
  dialogTitle: PropTypes.string.isRequired,
  dialogContent: PropTypes.string.isRequired
}

export default withStyles(styles)(SimpleDialog)
